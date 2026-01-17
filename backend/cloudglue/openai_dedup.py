import json
import re
from typing import Any, Dict, List, Tuple

import requests

from env_config import get_openai_api_key, get_openai_model
from intervals import merge_intervals, overlap_ratio, DEFAULT_MERGE_GAP_SECONDS

DEFAULT_OPENAI_TIMEOUT_SECONDS = 60
DEFAULT_TRACK_OVERLAP_THRESHOLD = 0.85


def openai_chat_json(system: str, user: str, timeout_seconds: int = DEFAULT_OPENAI_TIMEOUT_SECONDS) -> Dict[str, Any]:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {get_openai_api_key()}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": get_openai_model(),
        "temperature": 0,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=timeout_seconds)
    resp.raise_for_status()
    data = resp.json()
    content = data["choices"][0]["message"]["content"]

    try:
        return json.loads(content)
    except Exception:
        m = re.search(r"\{.*\}", content, flags=re.S)
        if not m:
            raise RuntimeError(f"OpenAI returned non-JSON content: {content[:400]}")
        return json.loads(m.group(0))


def gpt_dedup_and_filter(
    target_desc: str,
    inputs: List[Dict[str, Any]],
    timeout_seconds: int = DEFAULT_OPENAI_TIMEOUT_SECONDS,
) -> List[Dict[str, str]]:
    system = (
        "You clean up noisy object names extracted from video segments.\n"
        "Output only valid JSON.\n\n"
        "Goal:\n"
        "1) Remove hallucinations and wrong objects.\n"
        "2) Deduplicate synonyms that refer to the same physical object.\n"
        "3) Return a canonical name per kept item.\n"
        "4) If a generic name and a more specific instance name refer to the same physical object, keep only the more specific name.\n\n"
        "Hard constraints:\n"
        "- You must not invent new objects or new names.\n"
        "- canonical_name must be one of the input names.\n"
        "- Keep can and bottle distinct. Do not merge a can into a bottle or vice versa.\n"
        "- If both 'soda can' and 'red soda can' exist, map 'red soda can' to 'soda can'.\n"
        "- Use intervals and scene descriptions as evidence. Only merge generic into specific when they clearly refer to the same object.\n"
        "- If you are uncertain an item is real, mark keep=false.\n"
    )

    user = json.dumps(
        {
            "target_object_description": target_desc,
            "inputs": inputs,
            "output_format": {
                "items": [
                    {
                        "name": "one of the input names",
                        "keep": "boolean",
                        "canonical_name": "one of the input names",
                        "why": "short reason",
                    }
                ]
            },
        },
        ensure_ascii=False,
        indent=2,
    )

    out = openai_chat_json(system, user, timeout_seconds=timeout_seconds)
    arr = out.get("items")
    if not isinstance(arr, list):
        raise RuntimeError(f"Bad OpenAI response: {out}")

    allowed_names = {it["name"] for it in inputs}

    kept: List[Dict[str, str]] = []
    for row in arr:
        if not isinstance(row, dict):
            continue
        name = (row.get("name") or "").strip()
        canon = (row.get("canonical_name") or "").strip()
        keep = row.get("keep")

        if name not in allowed_names:
            continue
        if canon not in allowed_names:
            canon = name
        if keep is True:
            kept.append({"name": name, "canonical_name": canon})

    return kept


def apply_dedup_mapping_union_intervals(
    merged_by_name: Dict[str, Dict[str, Any]],
    kept_decisions: List[Dict[str, str]],
    merge_gap_seconds: float,
) -> List[Dict[str, Any]]:
    canon_to_members: Dict[str, List[str]] = {}
    for d in kept_decisions:
        canon_to_members.setdefault(d["canonical_name"], []).append(d["name"])

    tracks: List[Dict[str, Any]] = []
    for canon, members in canon_to_members.items():
        all_intervals: List[Tuple[float, float]] = []
        aliases = set()
        scene_descs: List[str] = []
        seen_desc = set()

        for m in members:
            info = merged_by_name.get(m)
            if not info:
                continue
            aliases.add(m)
            all_intervals.extend(info["intervals"])

            for d in info.get("scene_descriptions", []) or []:
                d = (d or "").strip()
                if d and d not in seen_desc:
                    seen_desc.add(d)
                    scene_descs.append(d)
                if len(scene_descs) >= 8:
                    break

        unioned = merge_intervals(all_intervals, merge_gap_seconds)
        tracks.append(
            {
                "object_name": canon,
                "aliases": sorted(aliases),
                "intervals": [{"start_time": round(st, 3), "end_time": round(et, 3)} for st, et in unioned],
                "scene_descriptions": scene_descs,
            }
        )

    tracks.sort(
        key=lambda t: (
            float(t["intervals"][0]["start_time"]) if t["intervals"] else 1e18,
            t["object_name"].lower(),
        )
    )
    return tracks


def _tracks_to_interval_tuples(track: Dict[str, Any]) -> List[Tuple[float, float]]:
    out: List[Tuple[float, float]] = []
    for iv in track.get("intervals", []) or []:
        try:
            out.append((float(iv["start_time"]), float(iv["end_time"])))
        except Exception:
            continue
    return out


def _resolve_mapping(name: str, mapping: Dict[str, str], allowed: set) -> str:
    cur = name
    for _ in range(20):
        nxt = mapping.get(cur, cur)
        if nxt not in allowed:
            return name
        if nxt == cur:
            return cur
        cur = nxt
    return cur


def gpt_merge_tracks_if_needed(
    target_desc: str,
    tracks: List[Dict[str, Any]],
    overlap_threshold: float = DEFAULT_TRACK_OVERLAP_THRESHOLD,
    timeout_seconds: int = DEFAULT_OPENAI_TIMEOUT_SECONDS,
    merge_gap_seconds: float = DEFAULT_MERGE_GAP_SECONDS,
) -> List[Dict[str, Any]]:
    if len(tracks) <= 1:
        return tracks

    tuples = [_tracks_to_interval_tuples(t) for t in tracks]
    total_pairs = 0
    suspicious_pairs = []
    for i in range(len(tracks)):
        for j in range(i + 1, len(tracks)):
            total_pairs += 1
            r = overlap_ratio(tuples[i], tuples[j])
            if r >= overlap_threshold:
                suspicious_pairs.append((i, j, r))

    if not suspicious_pairs:
        return tracks

    compact_tracks = []
    for t in tracks:
        compact_tracks.append(
            {
                "object_name": t.get("object_name", ""),
                "aliases": t.get("aliases", []) or [],
                "intervals": t.get("intervals", []) or [],
                "scene_descriptions": t.get("scene_descriptions", []) or [],
            }
        )

    system = (
        "You merge duplicate object tracks that refer to the same physical object in a video.\n"
        "Output only valid JSON.\n\n"
        "Guidelines:\n"
        "- Use time overlap and scene descriptions as evidence.\n"
        "- If one name is a specific instance of another (brand specific vs generic) and they refer to the same object, merge into the more specific name.\n"
        "- Do not merge different physical objects.\n"
        "- Do not invent new names. The merge target must be one of the existing object_name values.\n\n"
        "Output:\n"
        "- Provide a mapping merge_to where each key is an existing object_name and each value is the chosen canonical object_name.\n"
        "- Names not in merge_to map to themselves.\n"
    )

    user = json.dumps(
        {
            "target_object_description": target_desc,
            "tracks": compact_tracks,
            "high_overlap_pairs": [{"a": tracks[i]["object_name"], "b": tracks[j]["object_name"], "overlap_ratio": round(r, 3)} for i, j, r in suspicious_pairs],
            "output_format": {"merge_to": {"object_name": "canonical_object_name"}},
        },
        ensure_ascii=False,
        indent=2,
    )

    out = openai_chat_json(system, user, timeout_seconds=timeout_seconds)
    mapping = out.get("merge_to")
    if not isinstance(mapping, dict):
        return tracks

    allowed = {t["object_name"] for t in tracks}
    resolved: Dict[str, str] = {}
    for k, v in mapping.items():
        if isinstance(k, str) and isinstance(v, str) and k in allowed:
            resolved[k] = v

    groups: Dict[str, List[Dict[str, Any]]] = {}
    for t in tracks:
        name = t["object_name"]
        canon = _resolve_mapping(name, resolved, allowed)
        groups.setdefault(canon, []).append(t)

    merged_tracks: List[Dict[str, Any]] = []
    for canon, members in groups.items():
        all_intervals: List[Tuple[float, float]] = []
        aliases = set()
        scene_descs: List[str] = []
        seen_desc = set()

        for m in members:
            aliases.update(m.get("aliases", []) or [])
            for iv in m.get("intervals", []) or []:
                try:
                    all_intervals.append((float(iv["start_time"]), float(iv["end_time"])))
                except Exception:
                    continue
            for d in m.get("scene_descriptions", []) or []:
                d = (d or "").strip()
                if d and d not in seen_desc:
                    seen_desc.add(d)
                    scene_descs.append(d)

        unioned = merge_intervals(all_intervals, merge_gap_seconds)
        merged_tracks.append(
            {
                "object_name": canon,
                "aliases": sorted(aliases),
                "intervals": [{"start_time": round(st, 3), "end_time": round(et, 3)} for st, et in unioned],
                "scene_descriptions": scene_descs[:10],
            }
        )

    merged_tracks.sort(
        key=lambda t: (
            float(t["intervals"][0]["start_time"]) if t["intervals"] else 1e18,
            t["object_name"].lower(),
        )
    )
    return merged_tracks
