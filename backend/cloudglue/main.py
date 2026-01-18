from cloudglue_client import upload_video, create_extract_job, wait_until_completed
from gemini_target import describe_target_from_image
from mentions import collect_mentions, merge_by_exact_name_union_find, generic_filter_by_mentions_or_time
from intervals import DEFAULT_MERGE_GAP_SECONDS
from openai_dedup import (
    gpt_dedup_and_filter,
    apply_dedup_mapping_union_intervals,
    gpt_merge_tracks_if_needed,
)
from sam3 import sam3_segment_object_in_timerange


def main() -> None:
    VIDEO_PATH = "video.mp4"
    IMAGE_PATH = "target.jpg"

    print("Deriving target description from image...")
    target_desc = describe_target_from_image(IMAGE_PATH)
    print("Target:", target_desc)

    print("Uploading video...")
    video_url = upload_video(VIDEO_PATH)
    print("Uploaded:", video_url)

    print("Creating extract job...")
    job = create_extract_job(video_url=video_url, target_object_description=target_desc)
    job_id = job["job_id"]
    print("Job ID:", job_id)

    print("Waiting for completion...")
    result = wait_until_completed(job_id, on_status=lambda s: print("Job status:", s))

    print("Collecting mentions...")
    mentions = collect_mentions(result)
    print("Mentions:", len(mentions))

    print("Merging intervals by exact name...")
    merged_by_name = merge_by_exact_name_union_find(mentions, merge_gap_seconds=DEFAULT_MERGE_GAP_SECONDS)

    print("Generic filtering...")
    merged_by_name = generic_filter_by_mentions_or_time(merged_by_name)

    gpt_inputs = []
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

    print("Calling GPT to deduplicate and filter names...")
    kept = gpt_dedup_and_filter(target_desc=target_desc, inputs=gpt_inputs)

    print("Unioning timestamps for merged names...")
    tracks = apply_dedup_mapping_union_intervals(
        merged_by_name=merged_by_name,
        kept_decisions=kept,
        merge_gap_seconds=DEFAULT_MERGE_GAP_SECONDS,
    )

    print("Merging overlapping tracks if needed...")
    tracks = gpt_merge_tracks_if_needed(
        target_desc=target_desc,
        tracks=tracks,
        merge_gap_seconds=DEFAULT_MERGE_GAP_SECONDS,
    )

    print("Tracks:", len(tracks))
    for t in tracks:
        print("Object:", t["object_name"])
        print("Aliases:", t["aliases"])
        print("Intervals:", t["intervals"])
        descs = t.get("scene_descriptions", []) or []
        if descs:
            print("Scene:", descs[0])
        print()

    print("Driving Sam3Model...")
    for tr in tracks:
        obj_name = tr["object_name"]
        for iv in tr["intervals"]:
            sam3_segment_object_in_timerange(
                VIDEO_PATH,
                obj_name,
                float(iv["start_time"]),
                float(iv["end_time"]),
            )


if __name__ == "__main__":
    main()
