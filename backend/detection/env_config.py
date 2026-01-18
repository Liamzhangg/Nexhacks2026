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


def get_tokenc_api_key() -> str:
    _ensure_loaded()
    key = os.getenv("TOKENC_API")
    if not key:
        raise RuntimeError("Missing TOKENC_API in .env")
    return key


def tokenc_disabled() -> bool:
    _ensure_loaded()
    v = (os.getenv("TOKENC_DISABLE", "0") or "0").strip().lower()
    return v in {"1", "true", "yes", "y", "on"}


def get_tokenc_aggressiveness(default: float = 0.55) -> float:
    _ensure_loaded()
    raw = os.getenv("TOKENC_AGGRESSIVENESS", str(default))
    try:
        x = float(raw)
    except Exception:
        x = default
    if x < 0.0:
        x = 0.0
    if x > 1.0:
        x = 1.0
    return x
