import os
import time
from typing import Any, Callable, Dict, Optional

import requests

from env_config import get_cloudglue_api_key

BASE_URL_DEFAULT = "https://api.cloudglue.dev/v1"

DEFAULT_WINDOW_SECONDS = 1
DEFAULT_HOP_SECONDS = 1
DEFAULT_POLL_INTERVAL_SECONDS = 2

DEFAULT_REQUEST_TIMEOUT_SECONDS = 180
DEFAULT_STATUS_TIMEOUT_SECONDS = 60


def _auth_headers() -> Dict[str, str]:
    return {"Authorization": f"Bearer {get_cloudglue_api_key()}"}


def _json_headers() -> Dict[str, str]:
    h = _auth_headers()
    h["Content-Type"] = "application/json"
    return h


def upload_video(
    video_path: str,
    base_url: str = BASE_URL_DEFAULT,
    timeout_seconds: int = DEFAULT_REQUEST_TIMEOUT_SECONDS,
) -> str:
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")

    with open(video_path, "rb") as f:
        resp = requests.post(
            f"{base_url}/files",
            headers=_auth_headers(),
            files={"file": (os.path.basename(video_path), f, "video/mp4")},
            timeout=timeout_seconds,
        )
    resp.raise_for_status()
    file_id = resp.json()["id"]
    return f"cloudglue://files/{file_id}"


def create_extract_job(
    video_url: str,
    target_object_description: str,
    window_seconds: float = DEFAULT_WINDOW_SECONDS,
    hop_seconds: float = DEFAULT_HOP_SECONDS,
    base_url: str = BASE_URL_DEFAULT,
    timeout_seconds: int = DEFAULT_REQUEST_TIMEOUT_SECONDS,
) -> Dict[str, Any]:
    if window_seconds < 1 or hop_seconds < 1:
        raise ValueError("Cloudglue requires window_seconds >= 1 and hop_seconds >= 1")

    prompt = (
        "You are analyzing a video split into time segments.\n\n"
        f"Target object: {target_object_description}\n\n"
        "Task:\n"
        "For each segment, list objects that are clearly visible and could be replaced by the target object.\n"
        "Replacement means swapping the object with the target in the same place.\n\n"
        "For every listed object, return:\n"
        "- object_name: short canonical name\n"
        "- start_time, end_time: seconds (continuous visibility interval)\n"
        "- reason: why this object is a plausible replacement target\n"
        "- scene_description: 1-2 sentences describing the scene and where this object is in it\n\n"
        "Rules:\n"
        "- Do NOT output bounding boxes.\n"
        "- Do NOT invent objects.\n"
        "- If unsure, omit.\n"
        "- If none, output an empty list.\n"
        "- In each segment, list each distinct object_name at most once.\n"
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
                    "scene_description": "string",
                }
            ]
        },
        "enable_video_level_entities": False,
        "enable_segment_level_entities": True,
        "segmentation_config": {
            "strategy": "uniform",
            "uniform_config": {
                "window_seconds": window_seconds,
                "hop_seconds": hop_seconds,
            },
        },
    }

    resp = requests.post(
        f"{base_url}/extract",
        headers=_json_headers(),
        json=payload,
        timeout=timeout_seconds,
    )
    resp.raise_for_status()
    return resp.json()


def get_extract_job(
    job_id: str,
    base_url: str = BASE_URL_DEFAULT,
    timeout_seconds: int = DEFAULT_STATUS_TIMEOUT_SECONDS,
) -> Dict[str, Any]:
    resp = requests.get(f"{base_url}/extract/{job_id}", headers=_json_headers(), timeout=timeout_seconds)
    resp.raise_for_status()
    return resp.json()


def wait_until_completed(
    job_id: str,
    poll_interval_seconds: float = DEFAULT_POLL_INTERVAL_SECONDS,
    base_url: str = BASE_URL_DEFAULT,
    on_status: Optional[Callable[[str], None]] = None,
) -> Dict[str, Any]:
    while True:
        data = get_extract_job(job_id, base_url=base_url)
        status = data.get("status", "")
        if on_status:
            on_status(status)

        if status == "completed":
            return data
        if status in ("failed", "not_applicable"):
            raise RuntimeError(f"Extract failed: {data.get('error')}")

        time.sleep(poll_interval_seconds)
