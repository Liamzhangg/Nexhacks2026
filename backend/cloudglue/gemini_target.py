import base64
import os
from typing import Optional

import requests

from env_config import get_gemini_api_key

DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
DEFAULT_TIMEOUT_SECONDS = 60


def _guess_mime_type(path: str) -> str:
    p = path.lower()
    if p.endswith(".png"):
        return "image/png"
    if p.endswith(".webp"):
        return "image/webp"
    if p.endswith(".heic"):
        return "image/heic"
    if p.endswith(".heif"):
        return "image/heif"
    return "image/jpeg"


def _normalize_phrase(text: str) -> str:
    t = (text or "").strip().splitlines()[0].strip()
    t = t.strip('"').strip("'").strip()
    if not t:
        return "a product"
    lower = t.lower()
    if lower.startswith("a ") or lower.startswith("an "):
        return t
    return f"a {t}"


def describe_target_from_image(
    image_path: str,
    model: str = DEFAULT_GEMINI_MODEL,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> str:
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    api_key = get_gemini_api_key()
    mime = _guess_mime_type(image_path)

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    prompt = (
        "Look at the image and identify the main physical object or product.\n"
        "Return a short English noun phrase in the form: 'a ...' or 'an ...'.\n"
        "Use 3 to 6 words.\n"
        "Include brand if clearly visible.\n"
        "Output only the phrase, no punctuation, no extra text."
    )

    text = _try_google_genai_sdk(image_bytes, mime, prompt, model, timeout_seconds, api_key)
    if text is None:
        text = _try_rest(image_bytes, mime, prompt, model, timeout_seconds, api_key)

    return _normalize_phrase(text)


def _try_google_genai_sdk(
    image_bytes: bytes,
    mime: str,
    prompt: str,
    model: str,
    timeout_seconds: int,
    api_key: str,
) -> Optional[str]:
    try:
        from google import genai
        from google.genai import types
    except Exception:
        return None

    try:
        client = genai.Client(api_key=api_key)
        part = types.Part.from_bytes(data=image_bytes, mime_type=mime)
        resp = client.models.generate_content(
            model=model,
            contents=[part, prompt],
        )
        return getattr(resp, "text", None)
    except Exception:
        return None


def _try_rest(
    image_bytes: bytes,
    mime: str,
    prompt: str,
    model: str,
    timeout_seconds: int,
    api_key: str,
) -> str:
    b64 = base64.b64encode(image_bytes).decode("utf-8")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {"inline_data": {"mime_type": mime, "data": b64}},
                ]
            }
        ]
    }

    resp = requests.post(url, json=payload, timeout=timeout_seconds)
    resp.raise_for_status()
    data = resp.json()

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        raise RuntimeError(f"Unexpected Gemini REST response: {data}")
