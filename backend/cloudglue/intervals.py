from typing import List, Tuple

DEFAULT_MERGE_GAP_SECONDS = 0.30


def merge_intervals(intervals: List[Tuple[float, float]], gap: float) -> List[Tuple[float, float]]:
    if not intervals:
        return []
    xs = sorted(intervals, key=lambda x: (x[0], x[1]))
    out: List[Tuple[float, float]] = []
    cur_st, cur_et = xs[0]
    for st, et in xs[1:]:
        if st <= cur_et + gap:
            cur_et = max(cur_et, et)
        else:
            out.append((cur_st, cur_et))
            cur_st, cur_et = st, et
    out.append((cur_st, cur_et))
    return out


def interval_total_length(intervals: List[Tuple[float, float]]) -> float:
    return sum(max(0.0, et - st) for st, et in intervals)


def interval_intersection_length(a: List[Tuple[float, float]], b: List[Tuple[float, float]]) -> float:
    if not a or not b:
        return 0.0
    a = sorted(a, key=lambda x: (x[0], x[1]))
    b = sorted(b, key=lambda x: (x[0], x[1]))
    i = 0
    j = 0
    inter = 0.0
    while i < len(a) and j < len(b):
        st = max(a[i][0], b[j][0])
        et = min(a[i][1], b[j][1])
        if et > st:
            inter += (et - st)
        if a[i][1] < b[j][1]:
            i += 1
        else:
            j += 1
    return inter


def overlap_ratio(a: List[Tuple[float, float]], b: List[Tuple[float, float]]) -> float:
    la = interval_total_length(a)
    lb = interval_total_length(b)
    denom = min(la, lb)
    if denom <= 1e-9:
        return 0.0
    inter = interval_intersection_length(a, b)
    return inter / denom
