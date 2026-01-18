import os
import tempfile
import traceback
from typing import Any, Dict, Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from pipeline_runner import run_pipeline


app = FastAPI(title="Video Replaceability API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _save_upload_to_temp(upload: UploadFile, suffix: str) -> str:
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
        raise HTTPException(status_code=400, detail=f"Uploaded file '{upload.filename}' is empty")

    return path


def _safe_remove(path: Optional[str]) -> None:
    if not path:
        return
    try:
        os.remove(path)
    except Exception:
        pass


@app.post("/analyze")
def analyze(video: UploadFile = File(...), image: UploadFile = File(...)) -> JSONResponse:
    video_suffix = os.path.splitext(video.filename or "")[1] or ".mp4"
    image_suffix = os.path.splitext(image.filename or "")[1] or ".jpg"

    video_path: Optional[str] = None
    image_path: Optional[str] = None

    stage = "init"
    try:
        stage = "save_uploads"
        video_path = _save_upload_to_temp(video, suffix=video_suffix)
        image_path = _save_upload_to_temp(image, suffix=image_suffix)

        stage = "run_pipeline"
        result: Dict[str, Any] = run_pipeline(video_path=video_path, image_path=image_path)

        stage = "return"
        return JSONResponse(content=result)

    except HTTPException:
        raise
    except Exception as e:
        tb = traceback.format_exc()
        print("ERROR stage:", stage)
        print(tb)

        raise HTTPException(
            status_code=500,
            detail={
                "stage": stage,
                "error": str(e),
                "traceback": tb[-4000:],
            },
        )
    finally:
        _safe_remove(video_path)
        _safe_remove(image_path)
