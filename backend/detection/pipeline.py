import os
from typing import Any, Dict, List, Optional

from google.genai import types

from gemini_client import GeminiClient, generate_json, make_client, upload_file_and_wait_active
from tokenc_compress import compress_prompt


def _normalize_target_phrase(s: str) -> str:
    t = (s or "").strip().splitlines()[0].strip().strip('"').strip("'").strip()
    if not t:
        return "a product"
    lower = t.lower()
    if lower.startswith("a ") or lower.startswith("an "):
        return t
    return f"a {t}"


def describe_target_from_image(gc: GeminiClient, image_path: str) -> str:
    with open(image_path, "rb") as f:
        b = f.read()

    mime = "image/jpeg"
    p = image_path.lower()
    if p.endswith(".png"):
        mime = "image/png"
    elif p.endswith(".webp"):
        mime = "image/webp"
    elif p.endswith(".heic"):
        mime = "image/heic"
    elif p.endswith(".heif"):
        mime = "image/heif"

    prompt = (
        "Identify the main physical product or object in the image.\n"
        "Return JSON: {\"target\": \"a short noun phrase\"}.\n"
        "The phrase must start with 'a' or 'an'. Use 3 to 6 words. Include brand only if clearly visible.\n"
        "Output only JSON."
    )
    prompt = compress_prompt(prompt)

    data = generate_json(
        gc,
        [
            types.Part.from_bytes(data=b, mime_type=mime),
            types.Part(text=prompt),
        ],
    )

    target = ""
    if isinstance(data, dict):
        target = str(data.get("target", "")).strip()
    return _normalize_target_phrase(target)


def analyze_video(
    video_path: str,
    image_path: Optional[str] = None,
) -> Dict[str, Any]:
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")
    if image_path is not None and not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    gc = make_client()

    target_desc = None
    if image_path is not None:
        target_desc = describe_target_from_image(gc, image_path)

    video_file = upload_file_and_wait_active(gc, video_path)

    if target_desc is None:
        prompt = (
            "Analyze this video.\n"
            "List every distinct physical object that is clearly visible.\n"
            "For each object, provide one or more visibility intervals.\n\n"
            "Rules:\n"
            "Only include objects that actually appear.\n"
            "Do not invent objects.\n"
            "Merge adjacent intervals if the gap is <= 0.5 seconds.\n\n"
            "Return JSON only using this schema:\n"
            "{\n"
            "  \"items\": [\n"
            "    {\n"
            "      \"label\": \"string\",\n"
            "      \"description\": \"one sentence scene description including where the object is\",\n"
            "      \"timestamps\": [\n"
            "        {\"start_time\": number, \"end_time\": number}\n"
            "      ]\n"
            "    }\n"
            "  ]\n"
            "}\n"
        )
    else:
        prompt = (
            "Analyze this video.\n"
            f"Target object to insert or replace: {target_desc}\n\n"
            "Task:\n"
            "List every distinct visible object that could be replaced by the target object in the same physical location.\n"
            "Replacement means swapping what is there with the target in the same place.\n\n"
            "Rules:\n"
            "Only include objects that actually appear.\n"
            "Do not invent objects.\n"
            "If unsure, omit.\n"
            "Merge adjacent intervals if the gap is <= 0.5 seconds.\n\n"
            "Return JSON only using this schema:\n"
            "{\n"
            "  \"target\": \"string\",\n"
            "  \"items\": [\n"
            "    {\n"
            "      \"label\": \"string\",\n"
            "      \"description\": \"one sentence scene description including where the object is\",\n"
            "      \"timestamps\": [\n"
            "        {\"start_time\": number, \"end_time\": number}\n"
            "      ]\n"
            "    }\n"
            "  ]\n"
            "}\n"
        )

    prompt = compress_prompt(prompt)

    data = generate_json(
        gc,
        [
            video_file,
            types.Part(text=prompt),
        ],
    )

    out: Dict[str, Any] = {"items": []}
    if target_desc is not None:
        out["target"] = target_desc

    if isinstance(data, dict) and isinstance(data.get("items"), list):
        items: List[Dict[str, Any]] = []
        for it in data["items"]:
            if not isinstance(it, dict):
                continue
            label = str(it.get("label", "")).strip()
            desc = str(it.get("description", "")).strip()
            ts = it.get("timestamps")
            if not label or not isinstance(ts, list):
                continue
            cleaned = []
            for x in ts:
                if not isinstance(x, dict):
                    continue
                try:
                    st = float(x.get("start_time"))
                    et = float(x.get("end_time"))
                except Exception:
                    continue
                if et < st:
                    st, et = et, st
                cleaned.append({"start_time": round(st, 3), "end_time": round(et, 3)})
            if not cleaned:
                continue
            items.append({"label": label, "description": desc, "timestamps": cleaned})
        out["items"] = items

    return out
