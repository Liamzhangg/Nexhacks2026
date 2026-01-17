import cv2
import torch
import numpy as np
from accelerate import Accelerator
from transformers import Sam3TrackerVideoModel, Sam3TrackerVideoProcessor
from transformers.video_utils import load_video

VIDEO_PATH = "input.mp4"
OUTPUT_PATH = "output.mp4"

# ------------------------------------------------
# 鼠标点选
# ------------------------------------------------
def pick_points(frame_bgr):
    points = []
    labels = []

    win = "Left=positive Right=negative Enter=run r=reset q=quit"
    base = frame_bgr.copy()

    def redraw():
        img = base.copy()
        for (x, y), lab in zip(points, labels):
            color = (0, 255, 0) if lab == 1 else (0, 0, 255)
            cv2.circle(img, (x, y), 6, color, -1)
        cv2.imshow(win, img)

    def on_mouse(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            points.append((x, y))
            labels.append(1)
            redraw()
        elif event == cv2.EVENT_RBUTTONDOWN:
            points.append((x, y))
            labels.append(0)
            redraw()

    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(win, on_mouse)
    redraw()

    while True:
        k = cv2.waitKey(20) & 0xFF
        if k == ord("q"):
            raise SystemExit
        if k == ord("r"):
            points.clear()
            labels.clear()
            redraw()
        if k in (10, 13):  # Enter
            if len(points) == 0:
                print("至少点一个正样本")
                continue
            cv2.destroyWindow(win)
            return points, labels


def overlay(frame, mask, alpha=0.5):
    mask = mask > 0.5
    out = frame.copy()
    green = np.array([0, 255, 0], dtype=np.float32)
    pix = out[mask].astype(np.float32)
    out[mask] = ((1 - alpha) * pix + alpha * green).astype(np.uint8)
    return out


# ------------------------------------------------
# 主程序
# ------------------------------------------------
def main():
    accelerator = Accelerator()
    device = accelerator.device
    print("Using device:", device)

    model = Sam3TrackerVideoModel.from_pretrained(
        "facebook/sam3",
        token=True,
        torch_dtype=torch.bfloat16,
    ).to(device)

    processor = Sam3TrackerVideoProcessor.from_pretrained(
        "facebook/sam3",
        token=True,
    )

    model.eval()

    # 读视频帧
    video_frames, _ = load_video(VIDEO_PATH)
    if len(video_frames) == 0:
        raise RuntimeError("视频没有读到帧")

    # fps 一定用 OpenCV
    cap = cv2.VideoCapture(VIDEO_PATH)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()

    # 第一帧点选
    first_rgb = np.array(video_frames[0])
    first_bgr = cv2.cvtColor(first_rgb, cv2.COLOR_RGB2BGR)
    points_xy, labels01 = pick_points(first_bgr)

    points = [[[[int(x), int(y)] for (x, y) in points_xy]]]
    labels = [[[int(l) for l in labels01]]]

    # 初始化 session
    inference_session = processor.init_video_session(
        video=video_frames,
        inference_device=device,
        dtype=torch.bfloat16,
    )

    processor.add_inputs_to_inference_session(
        inference_session=inference_session,
        frame_idx=0,
        obj_ids=1,
        input_points=points,
        input_labels=labels,
    )

    # VideoWriter
    h, w = first_bgr.shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out_video = cv2.VideoWriter(OUTPUT_PATH, fourcc, fps, (w, h))

    # ---------- 第 0 帧 ----------
    with torch.no_grad():
        out0 = model(inference_session=inference_session, frame_idx=0)

    masks0 = processor.post_process_masks(
        [out0.pred_masks],
        original_sizes=[[inference_session.video_height,
                         inference_session.video_width]],
        binarize=False,
    )[0]

    m0 = masks0[0]
    while m0.ndim > 2:
        m0 = m0[0]
    m0 = m0.float().cpu().numpy()   # ✅ 关键修复

    frame0 = overlay(first_bgr, m0)
    out_video.write(frame0)
    cv2.imshow("SAM3", frame0)
    cv2.waitKey(1)

    # ---------- 全视频追踪 ----------
    with torch.no_grad():
        for outp in model.propagate_in_video_iterator(
            inference_session=inference_session,
            max_frame_num_to_track=len(video_frames),
        ):
            idx = outp.frame_idx
            if idx == 0:
                continue

            masks = processor.post_process_masks(
                [outp.pred_masks],
                original_sizes=[[inference_session.video_height,
                                 inference_session.video_width]],
                binarize=False,
            )[0]

            m = masks[0]
            while m.ndim > 2:
                m = m[0]
            m = m.float().cpu().numpy()   # ✅ 关键修复

            rgb = np.array(video_frames[idx])
            bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
            out_frame = overlay(bgr, m)

            out_video.write(out_frame)
            cv2.imshow("SAM3", out_frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    out_video.release()
    cv2.destroyAllWindows()
    print("Saved result to", OUTPUT_PATH)


if __name__ == "__main__":
    main()
