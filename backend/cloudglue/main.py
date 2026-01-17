import cv2
import torch
import numpy as np
from accelerate import Accelerator
from transformers import Sam3VideoModel, Sam3VideoProcessor
from transformers.video_utils import load_video

VIDEO_PATH = "input.mp4"
OUTPUT_PATH = "output.mp4"
TEXT_PROMPT = "a beverage bottle or can placed naturally in the scene"
MAX_SECONDS = 1.0
MASK_THRESHOLD = 0.5

def frame_to_bgr(frame):
    # frame may be PIL.Image or numpy RGB
    if hasattr(frame, "convert") and hasattr(frame, "size"):
        rgb = np.array(frame.convert("RGB"))
    else:
        rgb = np.array(frame)
    if rgb.ndim == 2:
        rgb = np.stack([rgb, rgb, rgb], axis=-1)
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

def squeeze_mask(mask):
    # mask could be [H,W] or [1,H,W] or [H,W,1] etc
    m = mask
    if isinstance(m, torch.Tensor):
        m = m.float().detach().cpu().numpy()
    else:
        m = np.array(m, dtype=np.float32)

    while m.ndim > 2:
        m = m[0]
    if m.ndim == 2:
        return m
    # fallback
    return m.reshape(m.shape[0], m.shape[1])

def overlay_mask(frame_bgr, mask_2d, alpha=0.5):
    h, w = frame_bgr.shape[:2]
    if mask_2d.shape[0] != h or mask_2d.shape[1] != w:
        mask_2d = cv2.resize(mask_2d, (w, h), interpolation=cv2.INTER_LINEAR)

    sel = mask_2d > MASK_THRESHOLD
    if not np.any(sel):
        return frame_bgr

    out = frame_bgr.copy()
    green = np.array([0, 255, 0], dtype=np.float32)
    pix = out[sel].astype(np.float32)
    out[sel] = ((1 - alpha) * pix + alpha * green).astype(np.uint8)
    return out

def main():
    accelerator = Accelerator()
    device = accelerator.device
    print("Using device:", device)

    model = Sam3VideoModel.from_pretrained(
        "facebook/sam3",
        token=True,
        torch_dtype=torch.bfloat16,
    ).to(device)
    processor = Sam3VideoProcessor.from_pretrained(
        "facebook/sam3",
        token=True,
    )
    model.eval()

    cap = cv2.VideoCapture(VIDEO_PATH)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    if not fps or fps <= 1e-6:
        fps = 30.0

    max_frames = max(1, int(round(fps * MAX_SECONDS)))

    video_frames, _ = load_video(VIDEO_PATH)
    video_frames = video_frames[:max_frames]
    print(f"Processing {len(video_frames)} frames (first {MAX_SECONDS}s)")

    inference_session = processor.init_video_session(
        video=video_frames,
        inference_device=device,
        processing_device="cpu",
        video_storage_device="cpu",
        dtype=torch.bfloat16,
    )

    inference_session = processor.add_text_prompt(
        inference_session=inference_session,
        text=TEXT_PROMPT,
    )

    outputs_per_frame = {}

    with torch.no_grad():
        for model_outputs in model.propagate_in_video_iterator(
            inference_session=inference_session,
            max_frame_num_to_track=len(video_frames),
        ):
            processed = processor.postprocess_outputs(
                inference_session,
                model_outputs,
            )
            outputs_per_frame[model_outputs.frame_idx] = processed

    # 视频尺寸从第一帧拿
    first_bgr = frame_to_bgr(video_frames[0])
    h, w = first_bgr.shape[:2]

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out_video = cv2.VideoWriter(OUTPUT_PATH, fourcc, float(fps), (w, h))

    total_found = 0

    for i in range(len(video_frames)):
        frame_bgr = frame_to_bgr(video_frames[i])
        out = outputs_per_frame.get(i, None)

        if out is not None:
            masks = out.get("masks", None)
            scores = out.get("scores", None)

            if masks is not None and len(masks) > 0:
                if scores is not None and len(scores) > 0:
                    best = int(torch.argmax(scores).item()) if isinstance(scores, torch.Tensor) else int(np.argmax(np.array(scores)))
                else:
                    best = 0

                mask2d = squeeze_mask(masks[best])
                frame_bgr = overlay_mask(frame_bgr, mask2d, alpha=0.5)
                total_found += 1

        out_video.write(frame_bgr)
        cv2.imshow("SAM3 first second", frame_bgr)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    out_video.release()
    cv2.destroyAllWindows()
    print("Saved result to", OUTPUT_PATH)
    print("Frames with at least one mask:", total_found, "/", len(video_frames))

if __name__ == "__main__":
    main()
