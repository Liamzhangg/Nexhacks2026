import os
import tempfile
import traceback
from typing import Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from pipeline import analyze_video


app = FastAPI(title="Gemini Video Understanding API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _save_upload(upload: UploadFile, suffix: str) -> str:
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)

    written = 0
    try:
        with open(path, "wb") as f:
            while True:
                chunk = upload.file.read(1024 * 1024)
                if not chunk:
                    break
                f.write(chunk)
                written += len(chunk)
    finally:
        try:
            upload.file.close()
        except Exception:
            pass

    if written <= 0:
        try:
            os.remove(path)
        except Exception:
            pass
        raise HTTPException(status_code=400, detail="Empty upload")
    return path


def _rm(path: Optional[str]) -> None:
    if not path:
        return
    try:
        os.remove(path)
    except Exception:
        pass


@app.post("/analyze")
def analyze(video: UploadFile = File(...), image: Optional[UploadFile] = File(None)) -> JSONResponse:
    video_path: Optional[str] = None
    image_path: Optional[str] = None
    stage = "init"

    try:
        stage = "save_video"
        video_suffix = os.path.splitext(video.filename or "")[1] or ".mp4"
        video_path = _save_upload(video, suffix=video_suffix)

        if image is not None:
            stage = "save_image"
            image_suffix = os.path.splitext(image.filename or "")[1] or ".jpg"
            image_path = _save_upload(image, suffix=image_suffix)

        stage = "analyze"
        result = analyze_video(video_path=video_path, image_path=image_path)

        return JSONResponse(content=result)

    except HTTPException:
        raise
    except Exception as e:
        tb = traceback.format_exc()
        print("ERROR stage:", stage)
        print(tb)
        raise HTTPException(
            status_code=500,
            detail={"stage": stage, "error": str(e), "traceback": tb[-4000:]},
        )
    finally:
        _rm(video_path)
        _rm(image_path)
