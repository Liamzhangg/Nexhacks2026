import hashlib
from typing import Optional

from tokenc import TokenClient

from env_config import get_tokenc_api_key, get_tokenc_aggressiveness, tokenc_disabled

_client: Optional[TokenClient] = None
_cache: dict[str, str] = {}


TOKENC_ENABLED = 1


def _get_client() -> TokenClient:
    global _client
    if _client is None:
        _client = TokenClient(api_key=get_tokenc_api_key())
    return _client


def compress_prompt(text: str) -> str:
    if not TOKENC_ENABLED:
        return text

    t = (text or "").strip()
    if not t:
        return text

    key = hashlib.sha256(t.encode("utf-8")).hexdigest()
    cached = _cache.get(key)
    if cached is not None:
        return cached

    try:
        client = _get_client()
        resp = client.compress_input(
            input=t,
            aggressiveness=get_tokenc_aggressiveness(),
        )
        out = (resp.output or "").strip()
        if not out:
            out = t
    except Exception:
        out = t

    _cache[key] = out
    return out
