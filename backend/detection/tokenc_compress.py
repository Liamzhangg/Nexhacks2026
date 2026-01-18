import hashlib
from typing import Optional

from tokenc import TokenClient

from env_config import get_tokenc_api_key

_CLIENT: Optional[TokenClient] = None
_CACHE: dict[str, str] = {}

AGGRESSIVENESS = 0.55


def _get_client() -> TokenClient:
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = TokenClient(api_key=get_tokenc_api_key())
    return _CLIENT


def compress_prompt(text: str) -> str:
    t = (text or "").strip()
    if not t:
        return text

    key = hashlib.sha256(t.encode("utf-8")).hexdigest()
    cached = _CACHE.get(key)
    if cached is not None:
        return cached

    try:
        client = _get_client()
        resp = client.compress_input(input=t, aggressiveness=AGGRESSIVENESS)
        out = (resp.output or "").strip()
        if not out:
            out = t
    except Exception:
        out = t

    _CACHE[key] = out
    return out
