from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pathlib import Path
from uuid import uuid4
import shutil

from ai_engine import AIEngine
from job_manager import job_manager


app = FastAPI(
    title="Story2Video AI Server",
    version="2.0.0"
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
        "version": "2.0.0"
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
# GET JOB STATUS
# =====================================================

@app.get("/v1/jobs/{job_id}")
def get_job(job_id: str):

    job = job_manager.get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found."
        )

    return job


# =====================================================
# BACKGROUND VIDEO PROCESSING
# =====================================================

def process_video_job(
    job_id: str,
    input_file: Path,
    prompt: str,
    mode: str,
    duration: int
):

    try:

        # ---------------------------------------------
        # JOB IS NOW PROCESSING
        # ---------------------------------------------

        job_manager.update_status(
            job_id,
            "processing"
        )

        # ---------------------------------------------
        # OUTPUT VIDEO PATH
        # ---------------------------------------------

        output_file = (
            OUTPUT_DIR /
            f"{job_id}.mp4"
        )

        # ---------------------------------------------
        # SEND JOB TO AI ENGINE
        # ---------------------------------------------

        result = ai_engine.generate(
            image_path=input_file,
            output_path=output_file,
            prompt=prompt,
            mode=mode,
            duration=duration
        )

        # ---------------------------------------------
        # CHECK RESULT
        # ---------------------------------------------

        if result is None:

            raise RuntimeError(
                "AI provider did not return a video."
            )

        # ---------------------------------------------
        # JOB COMPLETED
        # ---------------------------------------------

        video_url = (
            f"/storage/outputs/"
            f"{job_id}.mp4"
        )

        job_manager.update_status(
            job_id,
            "completed",
            video_url=video_url
        )


    except Exception as error:

        # ---------------------------------------------
        # JOB FAILED
        # ---------------------------------------------

        job_manager.update_status(
            job_id,
            "failed",
            error=str(error)
        )


# =====================================================
# IMAGE → VIDEO
# =====================================================

@app.post("/v1/image-to-video")
async def image_to_video(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(...),
    prompt: str = Form(""),
    mode: str = Form("AI Motion"),
    duration: int = Form(10)
):

    # ---------------------------------------------
    # VALIDATE IMAGE
    # ---------------------------------------------

    if image.content_type not in ALLOWED_IMAGE_TYPES:

        raise HTTPException(
            status_code=400,
            detail=(
                "Only JPEG, PNG and WebP images "
                "are supported."
            )
        )

    # ---------------------------------------------
    # VALIDATE DURATION
    # ---------------------------------------------

    if duration != 10:

        raise HTTPException(
            status_code=400,
            detail=(
                "Currently only 10-second videos "
                "are supported."
            )
        )

    # ---------------------------------------------
    # CREATE JOB ID
    # ---------------------------------------------

    job_id = str(uuid4())

    # ---------------------------------------------
    # CREATE JOB
    # ---------------------------------------------

    job_manager.create_job(
        job_id=job_id,
        prompt=prompt,
        mode=mode,
        duration=duration
    )

    # ---------------------------------------------
    # DETERMINE IMAGE EXTENSION
    # ---------------------------------------------

    extension = ".jpg"

    if image.content_type == "image/png":

        extension = ".png"

    elif image.content_type == "image/webp":

        extension = ".webp"

    # ---------------------------------------------
    # SAVE IMAGE
    # ---------------------------------------------

    input_file = (
        UPLOAD_DIR /
        f"{job_id}{extension}"
    )

    try:

        with input_file.open("wb") as buffer:

            shutil.copyfileobj(
                image.file,
                buffer
            )

    except Exception as error:

        job_manager.update_status(
            job_id,
            "failed",
            error=str(error)
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Could not save image: {error}"
            )
        )

    # ---------------------------------------------
    # ADD JOB TO BACKGROUND PROCESSING
    # ---------------------------------------------

    background_tasks.add_task(
        process_video_job,
        job_id,
        input_file,
        prompt,
        mode,
        duration
    )

    # ---------------------------------------------
    # RETURN JOB INFORMATION
    # ---------------------------------------------

    return JSONResponse(
        content={
            "success": True,
            "job_id": job_id,
            "status": "queued",
            "message": (
                "Your video job has been added "
                "to the Story2Video queue."
            ),
            "status_url": (
                f"/v1/jobs/{job_id}"
            )
        }
    )
