import json
import random
import re
import time
from dataclasses import dataclass
from typing import Any, Optional

from google import genai
from google.genai import types

from env_config import get_gemini_api_key, get_gemini_model


@dataclass
class GeminiClient:
    client: Any
    model: str


def make_client() -> GeminiClient:
    api_key = get_gemini_api_key()
    model = get_gemini_model()
    c = genai.Client(api_key=api_key)
    return GeminiClient(client=c, model=model)


def parse_json_maybe_fenced(text: str) -> Any:
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


def sleep_with_jitter(seconds: float) -> None:
    time.sleep(seconds + random.random() * 0.25)


def retryable(fn, *, max_retries: int = 6, base_backoff: float = 1.0, max_backoff: float = 30.0):
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
            backoff = min(max_backoff, base_backoff * (2 ** attempt))
            sleep_with_jitter(backoff)
    if last_exc:
        raise last_exc
    raise RuntimeError("Retry failed")


def upload_file_and_wait_active(gc: GeminiClient, path: str, poll_seconds: float = 2.0) -> Any:
    video_file = retryable(lambda: gc.client.files.upload(file=path))

    def _wait() -> Any:
        while True:
            info = gc.client.files.get(name=video_file.name)
            state = getattr(info, "state", None)
            state_name = getattr(state, "name", None) if state is not None else None
            if state_name == "ACTIVE":
                return video_file
            if state_name == "FAILED":
                raise RuntimeError("Gemini file processing failed")
            sleep_with_jitter(poll_seconds)

    return retryable(_wait, max_retries=0)


def generate_json(gc: GeminiClient, contents: list[Any]) -> Any:
    config = types.GenerateContentConfig(response_mime_type="application/json")

    def _call() -> Any:
        resp = gc.client.models.generate_content(
            model=gc.model,
            contents=contents,
            config=config,
        )
        text = getattr(resp, "text", None)
        if not text:
            raise RuntimeError("Gemini returned empty text")
        return parse_json_maybe_fenced(text)

    return retryable(_call)
