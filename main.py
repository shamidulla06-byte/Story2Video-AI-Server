from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from uuid import uuid4
import shutil

from ai_engine import AIEngine


app = FastAPI(
    title="Story2Video AI Server",
    version="1.1.0"
)


# =====================================================
# DIRECTORIES
# =====================================================

BASE_DIR = Path(__file__).resolve().parent

UPLOAD_DIR = BASE_DIR / "storage" / "uploads"
OUTPUT_DIR = BASE_DIR / "storage" / "outputs"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# =====================================================
# AI ENGINE
# =====================================================

ai_engine = AIEngine()


# =====================================================
# ALLOWED IMAGE TYPES
# =====================================================

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp"
}


# =====================================================
# ROOT
# =====================================================

@app.get("/")
def root():
    return {
        "service": "Story2Video AI Server",
        "status": "online",
        "version": "1.1.0",
        "ai_engine": ai_engine.status()
    }


# =====================================================
# HEALTH CHECK
# =====================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "ai_engine": ai_engine.status()
    }


# =====================================================
# AI ENGINE STATUS
# =====================================================

@app.get("/v1/engine/status")
def engine_status():
    return ai_engine.status()


# =====================================================
# IMAGE → VIDEO
# =====================================================

@app.post("/v1/image-to-video")
async def image_to_video(
    image: UploadFile = File(...),
    prompt: str = Form(""),
    mode: str = Form("AI Motion"),
    duration: int = Form(10)
):

    # Validate image type

    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG, PNG and WebP images are supported."
        )

    # Validate duration

    if duration != 10:
        raise HTTPException(
            status_code=400,
            detail="Currently only 10-second videos are supported."
        )

    # Create Job ID

    job_id = str(uuid4())

    # File extension

    extension = ".jpg"

    if image.content_type == "image/png":
        extension = ".png"

    elif image.content_type == "image/webp":
        extension = ".webp"


    # Save uploaded image

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


    # Output video path

    output_file = OUTPUT_DIR / f"{job_id}.mp4"


    # =================================================
    # CALL OUR AI ENGINE
    # =================================================

    try:

        result = ai_engine.generate(
            image_path=input_file,
            output_path=output_file,
            prompt=prompt,
            mode=mode,
            duration=duration
        )

        return JSONResponse(
            content={
                "success": True,
                "job_id": job_id,
                "status": "completed",
                "video_file": str(result),
                "message": "Video generated successfully."
            }
        )

    except RuntimeError as error:

        # AI Model এখনও connected না থাকলে
        # Server crash করবে না

        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "job_id": job_id,
                "status": "engine_not_connected",
                "message": str(error),
                "engine_status": ai_engine.status()
            }
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Video generation failed: {error}"
        )
