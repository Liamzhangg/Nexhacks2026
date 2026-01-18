import json
import random
import re
import time
from typing import Any, Optional

from google import genai
from google.genai import types

from env_config import get_gemini_video_api_key, get_gemini_image_api_key


VIDEO_MODEL = "models/gemini-3-flash-preview"
IMAGE_MODEL = "models/gemini-3-flash-preview"

_DEFAULT_MAX_RETRIES = 6
_DEFAULT_BASE_BACKOFF_SECONDS = 1.0
_DEFAULT_MAX_BACKOFF_SECONDS = 30.0


_video_client: Optional[Any] = None
_image_client: Optional[Any] = None


def make_video_client() -> Any:
    global _video_client
    if _video_client is None:
        _video_client = genai.Client(api_key=get_gemini_video_api_key())
    return _video_client


def make_image_client() -> Any:
    global _image_client
    if _image_client is None:
        _image_client = genai.Client(api_key=get_gemini_image_api_key())
    return _image_client


def _parse_json_maybe_fenced(text: str) -> Any:
    t = (text or "").strip()
    if not t:
        raise ValueError("Empty model response")

    if t.startswith("```"):
        lines = t.splitlines()
        start = 0
        for i, line in enumerate(lines):
            if line.strip().startswith("```"):
                start = i + 1
                break
        end = len(lines)
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip().startswith("```"):
                end = i
                break
        t = "\n".join(lines[start:end]).strip()

    try:
        return json.loads(t)
    except Exception:
        m = re.search(r"\{.*\}", t, flags=re.S)
        if not m:
            raise
        return json.loads(m.group(0))


def _sleep_with_jitter(seconds: float) -> None:
    time.sleep(seconds + random.random() * 0.25)


def _retryable(fn, *, max_retries: int = _DEFAULT_MAX_RETRIES):
    last_exc: Optional[Exception] = None
    for attempt in range(max_retries + 1):
        try:
            return fn()
        except Exception as e:
            last_exc = e
            msg = str(e).lower()
            is_rate = "429" in msg or "too many requests" in msg or "rate" in msg
            is_temp = "503" in msg or "500" in msg or "timeout" in msg or "temporarily" in msg
            if attempt == max_retries or (not is_rate and not is_temp):
                raise
            backoff = min(_DEFAULT_MAX_BACKOFF_SECONDS, _DEFAULT_BASE_BACKOFF_SECONDS * (2 ** attempt))
            _sleep_with_jitter(backoff)
    if last_exc is not None:
        raise last_exc
    raise RuntimeError("Retry failed unexpectedly")


def upload_file_and_wait_active(client: Any, path: str, poll_seconds: float = 2.0) -> Any:
    uploaded = _retryable(lambda: client.files.upload(file=path))

    def _wait() -> Any:
        while True:
            info = client.files.get(name=uploaded.name)
            state = getattr(info, "state", None)
            state_name = getattr(state, "name", None) if state is not None else None
            if state_name == "ACTIVE":
                return uploaded
            if state_name == "FAILED":
                raise RuntimeError("Gemini file processing failed")
            _sleep_with_jitter(poll_seconds)

    return _wait()


def generate_json(client: Any, model: str, contents: list[Any]) -> Any:
    config = types.GenerateContentConfig(response_mime_type="application/json")

    def _call() -> Any:
        resp = client.models.generate_content(
            model=model,
            contents=contents,
            config=config,
        )
        text = getattr(resp, "text", None)
        if not text:
            raise RuntimeError("Gemini returned empty text")
        return _parse_json_maybe_fenced(text)

    return _retryable(_call)
