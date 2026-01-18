import json
import os

from pipeline import analyze_video


def main() -> None:
    video_path = "video2.mp4"
    image_path = "target.jpg"

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Missing {video_path} in the current directory")

    if not os.path.exists(image_path):
        image_path = None

    result = analyze_video(video_path=video_path, image_path=image_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
