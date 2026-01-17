import os
import time
import json
from typing import Any, Dict, List, Tuple
import requests
from dotenv import load_dotenv

# =======================
# User config
# =======================
BASE_URL = "https://api.cloudglue.dev/v1"
VIDEO_PATH = "input.mp4"

# This is the only input you need to change for the Cloudglue part.
# Examples:
# TARGET_OBJECT_DESCRIPTION = "a Coca-Cola bottle"
# TARGET_OBJECT_DESCRIPTION = "a Nike logo"
# TARGET_OBJECT_DESCRIPTION = "a wooden dining table"
TARGET_OBJECT_DESCRIPTION = "a Coca-Cola bottle"

# Segmentation. Cloudglue requires window_seconds >= 1 and hop_seconds >= 1.
WINDOW_SECONDS = 2
HOP_SECONDS = 1

# Polling. This only controls how often we check job status.
POLL_INTERVAL_SECONDS = 2

# Output report
OUTPUT_JSON_PATH = "replaceable_objects.json"

# =======================
# Auth
# =======================
load_dotenv()
API_KEY = os.getenv("CLOUDGLUE_API")
if not API_KEY:
    raise RuntimeError("Missing CLOUDGLUE_API in .env")

AUTH_HEADERS = {"Authorization": f"Bearer {API_KEY}"}
JSON_HEADERS = {**AUTH_HEADERS, "Content-Type": "application/json"}

if WINDOW_SECONDS < 1 or HOP_SECONDS < 1:
    raise ValueError("WINDOW_SECONDS and HOP_SECONDS must be >= 1 due to Cloudglue API constraints.")


# =======================
# Cloudglue API helpers
# =======================
def upload_video(path: str) -> str:
    """
    Uploads a local video to Cloudglue and returns cloudglue://files/<id>.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Video not found: {path}")

    with open(path, "rb") as f:
        resp = requests.post(
            f"{BASE_URL}/files",
            headers=AUTH_HEADERS,
            files={"file": (os.path.basename(path), f, "video/mp4")},
            timeout=180,
        )
    resp.raise_for_status()
    file_id = resp.json()["id"]
    return f"cloudglue://files/{file_id}"


def create_extract(video_url: str) -> Dict[str, Any]:
    """
    Creates an extract job that returns, per segment, a list of replaceable objects
    with their names and time intervals.
    """
    prompt = (
        "You are analyzing a video.\n\n"
        f"The target object is: {TARGET_OBJECT_DESCRIPTION}\n\n"
        "Your task is to identify ALL objects in the video that could be replaced by the target object.\n"
        "Replacement here means the existing object could be removed and the target object could appear in its place.\n"
        "Focus on physical replaceability rather than realism.\n\n"
        "For each replaceable object, output:\n"
        "- object_name: what the object is\n"
        "- start_time and end_time: the time interval in seconds during which it appears continuously\n\n"
        "Rules:\n"
        "- Do NOT output bounding boxes or coordinates.\n"
        "- Do NOT judge whether replacement is good or bad.\n"
        "- Only list objects that actually appear in the video.\n"
        "- If no replaceable objects appear, output an empty list.\n"
    )

    payload = {
        "url": video_url,
        "prompt": prompt,
        "schema": {
            "replaceable_objects": [
                {
                    "object_name": "string",
                    "start_time": "number",
                    "end_time": "number",
                    "reason": "string",
                }
            ]
        },
        "enable_video_level_entities": False,
        "enable_segment_level_entities": True,
        "segmentation_config": {
            "strategy": "uniform",
            "uniform_config": {
                "window_seconds": WINDOW_SECONDS,
                "hop_seconds": HOP_SECONDS,
            },
        },
    }

    resp = requests.post(f"{BASE_URL}/extract", headers=JSON_HEADERS, json=payload, timeout=180)
    resp.raise_for_status()
    return resp.json()


def get_extract(job_id: str) -> Dict[str, Any]:
    """
    Gets the extract job status and data.
    Cloudglue commonly exposes GET /extract/{job_id} even if the snippet only shows POST.
    """
    resp = requests.get(f"{BASE_URL}/extract/{job_id}", headers=JSON_HEADERS, timeout=60)
    resp.raise_for_status()
    return resp.json()


def wait_until_completed(job_id: str) -> Dict[str, Any]:
    while True:
        data = get_extract(job_id)
        status = data.get("status")
        print("Job status:", status)

        if status == "completed":
            return data
        if status in ("failed", "not_applicable"):
            raise RuntimeError(f"Extract failed: {data.get('error')}")

        time.sleep(POLL_INTERVAL_SECONDS)


# =======================
# Postprocessing helpers
# =======================
def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def collect_candidates(extract_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Collect replaceable_objects from all segments.
    Returns a flat list of dicts: {object_name, start_time, end_time, reason}.
    """
    data = extract_result.get("data") or {}
    segments = data.get("segment_entities") or []

    out: List[Dict[str, Any]] = []
    for seg in segments:
        entities = seg.get("entities") or {}
        objs = entities.get("replaceable_objects") or []
        if not isinstance(objs, list):
            continue

        for o in objs:
            if not isinstance(o, dict):
                continue
            name = (o.get("object_name") or "").strip()
            if not name:
                continue
            st = _safe_float(o.get("start_time"), default=_safe_float(seg.get("start_time"), 0.0))
            et = _safe_float(o.get("end_time"), default=_safe_float(seg.get("end_time"), st))
            if et < st:
                st, et = et, st
            reason = (o.get("reason") or "").strip()
            out.append({"object_name": name, "start_time": st, "end_time": et, "reason": reason})

    return out


def merge_intervals(items: List[Dict[str, Any]], merge_gap_seconds: float = 0.3) -> List[Dict[str, Any]]:
    """
    Merges overlapping or nearly touching intervals per object_name.
    """
    by_name: Dict[str, List[Tuple[float, float, str]]] = {}
    for it in items:
        name = it["object_name"]
        st = float(it["start_time"])
        et = float(it["end_time"])
        reason = it.get("reason", "")
        by_name.setdefault(name, []).append((st, et, reason))

    merged: List[Dict[str, Any]] = []
    for name, intervals in by_name.items():
        intervals.sort(key=lambda x: (x[0], x[1]))
        cur_st, cur_et, cur_reason = intervals[0]

        reasons = []
        if cur_reason:
            reasons.append(cur_reason)

        for st, et, reason in intervals[1:]:
            if st <= cur_et + merge_gap_seconds:
                cur_et = max(cur_et, et)
                if reason:
                    reasons.append(reason)
            else:
                merged.append(
                    {
                        "object_name": name,
                        "start_time": round(cur_st, 3),
                        "end_time": round(cur_et, 3),
                        "reason": "; ".join(reasons[:3]),
                    }
                )
                cur_st, cur_et = st, et
                reasons = [reason] if reason else []

        merged.append(
            {
                "object_name": name,
                "start_time": round(cur_st, 3),
                "end_time": round(cur_et, 3),
                "reason": "; ".join(reasons[:3]),
            }
        )

    merged.sort(key=lambda x: (x["start_time"], x["end_time"], x["object_name"].lower()))
    return merged


# =======================
# Sam3Model integration hook
# =======================
def sam3_segment_object_in_timerange(video_path: str, object_description: str, start_time: float, end_time: float) -> None:
    """
    Hook for your Sam3Model. Replace the body of this function with your real call.

    You said your Sam3Model takes an item description and automatically segments it in the video.
    You also want time ranges. You can pass start_time and end_time into your pipeline here.

    For now, this prints what would be segmented.
    """
    print(f"[Sam3Model] segment '{object_description}' from {start_time:.2f}s to {end_time:.2f}s")


# =======================
# Main
# =======================
if __name__ == "__main__":
    print("Uploading video...")
    video_url = upload_video(VIDEO_PATH)
    print("Uploaded:", video_url)

    print("Creating extract job...")
    job = create_extract(video_url)
    job_id = job["job_id"]
    print("Job ID:", job_id)

    print("Waiting for completion...")
    result = wait_until_completed(job_id)

    print("Collecting candidates...")
    raw_candidates = collect_candidates(result)
    merged = merge_intervals(raw_candidates)

    report = {
        "target_object_description": TARGET_OBJECT_DESCRIPTION,
        "video_url": video_url,
        "window_seconds": WINDOW_SECONDS,
        "hop_seconds": HOP_SECONDS,
        "results": merged,
    }

    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"Saved report to {OUTPUT_JSON_PATH}")
    print(f"Found {len(merged)} replaceable object intervals.")

    # Drive Sam3Model using Cloudglue suggestions
    for item in merged:
        sam3_segment_object_in_timerange(
            VIDEO_PATH,
            item["object_name"],
            float(item["start_time"]),
            float(item["end_time"]),
        )
