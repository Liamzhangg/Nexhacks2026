import os
import tempfile
from typing import Any, Dict

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from pipeline_runner import run_pipeline

app = FastAPI(title="Video Replaceability API")


def _save_upload_to_temp(upload: UploadFile, suffix: str) -> str:
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    try:
        with open(path, "wb") as f:
            while True:
                chunk = upload.file.read(1024 * 1024)
                if not chunk:
                    break
                f.write(chunk)
    finally:
        try:
            upload.file.close()
        except Exception:
            pass
    return path


@app.post("/analyze")
def analyze(video: UploadFile = File(...), image: UploadFile = File(...)) -> JSONResponse:
    video_suffix = os.path.splitext(video.filename or "")[1] or ".mp4"
    image_suffix = os.path.splitext(image.filename or "")[1] or ".jpg"

    video_path = ""
    image_path = ""
    try:
        video_path = _save_upload_to_temp(video, suffix=video_suffix)
        image_path = _save_upload_to_temp(image, suffix=image_suffix)

        result: Dict[str, Any] = run_pipeline(video_path=video_path, image_path=image_path)
        return JSONResponse(content=result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if video_path:
            try:
                os.remove(video_path)
            except Exception:
                pass
        if image_path:
            try:
                os.remove(image_path)
            except Exception:
                pass
