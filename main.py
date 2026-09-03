from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from uuid import uuid4
import shutil


app = FastAPI(
    title="Story2Video AI Server",
    version="1.0.0"
)


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "storage" / "uploads"
OUTPUT_DIR = BASE_DIR / "storage" / "outputs"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp"
}


@app.get("/")
def root():
    return {
        "service": "Story2Video AI Server",
        "status": "online",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "ai_engine": "not_connected"
    }


@app.post("/v1/image-to-video")
async def image_to_video(
    image: UploadFile = File(...),
    prompt: str = Form(""),
    duration: int = Form(10)
):

    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG, PNG and WebP images are supported."
        )

    if duration != 10:
        raise HTTPException(
            status_code=400,
            detail="Story2Video supports only 10-second videos."
        )

    job_id = str(uuid4())

    extension = ".jpg"

    if image.content_type == "image/png":
        extension = ".png"
    elif image.content_type == "image/webp":
        extension = ".webp"

    input_file = UPLOAD_DIR / f"{job_id}{extension}"

    try:

        with input_file.open("wb") as buffer:
            shutil.copyfileobj(
                image.file,
                buffer
            )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Could not save image: {error}"
        )

    return JSONResponse(
        content={
            "success": True,
            "job_id": job_id,
            "status": "queued",
            "message": (
                "Image received successfully. "
                "AI video generation engine will process this job."
            ),
            "duration": 10,
            "prompt": prompt,
            "video_url": None
        }
    )
