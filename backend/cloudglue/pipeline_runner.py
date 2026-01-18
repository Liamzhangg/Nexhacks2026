from typing import Any, Dict, List

from cloudglue_client import upload_video, create_extract_job, wait_until_completed
from gemini_target import describe_target_from_image
from mentions import collect_mentions, merge_by_exact_name_union_find, generic_filter_by_mentions_or_time
from intervals import DEFAULT_MERGE_GAP_SECONDS
from openai_dedup import (
    gpt_dedup_and_filter,
    apply_dedup_mapping_union_intervals,
    gpt_merge_tracks_if_needed,
)


def run_pipeline(video_path: str, image_path: str) -> Dict[str, Any]:
    target_desc = describe_target_from_image(image_path)

    video_url = upload_video(video_path)

    job = create_extract_job(video_url=video_url, target_object_description=target_desc)
    job_id = job["job_id"]

    result = wait_until_completed(job_id)

    mentions = collect_mentions(result)

    merged_by_name = merge_by_exact_name_union_find(mentions, merge_gap_seconds=DEFAULT_MERGE_GAP_SECONDS)
    merged_by_name = generic_filter_by_mentions_or_time(merged_by_name)

    gpt_inputs: List[Dict[str, Any]] = []
    for name, info in merged_by_name.items():
        gpt_inputs.append(
            {
                "name": name,
                "mention_count": int(info["mention_count"]),
                "total_visible_seconds": round(float(info["total_visible_seconds"]), 3),
                "intervals": [[round(st, 3), round(et, 3)] for st, et in info["intervals"]],
                "scene_descriptions": info.get("scene_descriptions", []) or [],
            }
        )
    gpt_inputs.sort(key=lambda x: x["name"].lower())

    kept = gpt_dedup_and_filter(target_desc=target_desc, inputs=gpt_inputs)

    tracks = apply_dedup_mapping_union_intervals(
        merged_by_name=merged_by_name,
        kept_decisions=kept,
        merge_gap_seconds=DEFAULT_MERGE_GAP_SECONDS,
    )

    tracks = gpt_merge_tracks_if_needed(
        target_desc=target_desc,
        tracks=tracks,
        merge_gap_seconds=DEFAULT_MERGE_GAP_SECONDS,
    )

    items = []
    for t in tracks:
        descs = t.get("scene_descriptions", []) or []
        description = descs[0] if descs else ""
        items.append(
            {
                "label": t.get("object_name", ""),
                "description": description,
                "timestamps": t.get("intervals", []) or [],
            }
        )

    return {
        "target_description": target_desc,
        "items": items,
    }
