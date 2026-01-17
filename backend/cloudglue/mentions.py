from typing import Any, Dict, List, Tuple

from union_find import UnionFind
from intervals import merge_intervals, interval_total_length

DEFAULT_MIN_MENTIONS = 2
DEFAULT_MIN_TOTAL_VISIBLE_SECONDS = 0.8
DEFAULT_KEEP_IF_VISIBLE_SECONDS_AT_LEAST = 2.0


def _sf(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def collect_mentions(extract_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    data = extract_result.get("data") or {}
    segments = data.get("segment_entities") or []

    out: List[Dict[str, Any]] = []
    for seg in segments:
        seg_st = _sf(seg.get("start_time"), 0.0)
        seg_et = _sf(seg.get("end_time"), seg_st)

        entities = seg.get("entities") or {}
        objs = entities.get("replaceable_objects") or []
        if not isinstance(objs, list):
            continue

        seen = set()
        for o in objs:
            if not isinstance(o, dict):
                continue
            name = (o.get("object_name") or "").strip()
            if not name or name in seen:
                continue
            seen.add(name)

            st = _sf(o.get("start_time"), seg_st)
            et = _sf(o.get("end_time"), seg_et)
            if et < st:
                st, et = et, st

            reason = (o.get("reason") or "").strip()
            scene_description = (o.get("scene_description") or "").strip()

            out.append(
                {
                    "object_name": name,
                    "start_time": st,
                    "end_time": et,
                    "reason": reason,
                    "scene_description": scene_description,
                }
            )

    return out


def merge_by_exact_name_union_find(
    mentions: List[Dict[str, Any]],
    merge_gap_seconds: float,
) -> Dict[str, Dict[str, Any]]:
    by_name: Dict[str, List[int]] = {}
    for i, m in enumerate(mentions):
        by_name.setdefault(m["object_name"], []).append(i)

    out: Dict[str, Dict[str, Any]] = {}

    for name, idxs in by_name.items():
        idxs_sorted = sorted(idxs, key=lambda j: (mentions[j]["start_time"], mentions[j]["end_time"]))
        uf = UnionFind(len(idxs_sorted))

        prev_end = float(mentions[idxs_sorted[0]]["end_time"])
        prev_k = 0
        for k in range(1, len(idxs_sorted)):
            st = float(mentions[idxs_sorted[k]]["start_time"])
            et = float(mentions[idxs_sorted[k]]["end_time"])
            if st <= prev_end + merge_gap_seconds:
                uf.union(prev_k, k)
                prev_end = max(prev_end, et)
            else:
                prev_k = k
                prev_end = et

        comp: Dict[int, Tuple[float, float]] = {}
        for k, orig_idx in enumerate(idxs_sorted):
            root = uf.find(k)
            st = float(mentions[orig_idx]["start_time"])
            et = float(mentions[orig_idx]["end_time"])
            if root not in comp:
                comp[root] = (st, et)
            else:
                a, b = comp[root]
                comp[root] = (min(a, st), max(b, et))

        intervals = sorted(list(comp.values()), key=lambda x: (x[0], x[1]))
        intervals = merge_intervals(intervals, 0.0)

        scene_descs: List[str] = []
        seen_desc = set()
        for idx in idxs:
            d = (mentions[idx].get("scene_description") or "").strip()
            if d and d not in seen_desc:
                seen_desc.add(d)
                scene_descs.append(d)
            if len(scene_descs) >= 6:
                break

        out[name] = {
            "intervals": intervals,
            "mention_count": len(idxs),
            "total_visible_seconds": interval_total_length(intervals),
            "scene_descriptions": scene_descs,
        }

    return out


def generic_filter_by_mentions_or_time(
    merged_by_name: Dict[str, Dict[str, Any]],
    min_mentions: int = DEFAULT_MIN_MENTIONS,
    min_total_visible_seconds: float = DEFAULT_MIN_TOTAL_VISIBLE_SECONDS,
    keep_if_visible_seconds_at_least: float = DEFAULT_KEEP_IF_VISIBLE_SECONDS_AT_LEAST,
) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for name, info in merged_by_name.items():
        mentions = int(info.get("mention_count", 0))
        total_sec = float(info.get("total_visible_seconds", 0.0))

        if total_sec < min_total_visible_seconds:
            continue
        if mentions >= min_mentions or total_sec >= keep_if_visible_seconds_at_least:
            out[name] = info

    return out
