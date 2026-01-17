import os
from dotenv import load_dotenv

_loaded = False


def _ensure_loaded() -> None:
    global _loaded
    if not _loaded:
        load_dotenv()
        _loaded = True


def get_cloudglue_api_key() -> str:
    _ensure_loaded()
    key = os.getenv("CLOUDGLUE_API")
    if not key:
        raise RuntimeError("Missing CLOUDGLUE_API in .env")
    return key


def get_openai_api_key() -> str:
    _ensure_loaded()
    key = os.getenv("OPENAI_API")
    if not key:
        raise RuntimeError("Missing OPENAI_API in .env")
    return key


def get_openai_model(default: str = "gpt-4o-mini") -> str:
    _ensure_loaded()
    return os.getenv("OPENAI_MODEL", default)
