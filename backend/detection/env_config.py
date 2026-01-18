import os
from dotenv import load_dotenv

_loaded = False


def _ensure_loaded() -> None:
    global _loaded
    if not _loaded:
        load_dotenv()
        _loaded = True


def get_gemini_video_api_key() -> str:
    _ensure_loaded()
    key = os.getenv("GEMINI_VIDEO_API")
    if not key:
        raise RuntimeError("Missing GEMINI_VIDEO_API in .env")
    return key


def get_gemini_image_api_key() -> str:
    _ensure_loaded()
    key = os.getenv("GEMINI_IMAGE_API")
    if not key:
        raise RuntimeError("Missing GEMINI_IMAGE_API in .env")
    return key


def get_tokenc_api_key() -> str:
    _ensure_loaded()
    key = os.getenv("TOKENC_API")
    if not key:
        raise RuntimeError("Missing TOKENC_API in .env")
    return key
