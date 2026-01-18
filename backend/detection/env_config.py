import os
from dotenv import load_dotenv

_loaded = False


def _ensure_loaded() -> None:
    global _loaded
    if not _loaded:
        load_dotenv()
        _loaded = True


def get_gemini_api_key() -> str:
    _ensure_loaded()
    key = os.getenv("GEMINI_API")
    if not key:
        raise RuntimeError("Missing GEMINI_API in .env")
    return key


def get_gemini_model(default: str = "gemini-3-flash-preview") -> str:
    _ensure_loaded()
    return os.getenv("GEMINI_MODEL", default)
