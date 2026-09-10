from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    HTTPException,
    BackgroundTasks
)
from fastapi.responses import JSONResponse
from pathlib import Path
from uuid import uuid4
import shutil
import traceback
import logging

from ai_engine import AIEngine
from job_manager import job_manager
from story_intelligence import story_intelligence
from scene_planner import scene_planner
from continuity_engine import continuity_engine


# =====================================================
# LOGGING
# =====================================================

logging.basicConfig(
    level=logging.INFO
)

logger = logging.getLogger("story2video")


# =====================================================
# APP
# =====================================================

app = FastAPI(
    title="Story2Video AI Server",
    version="2.4.0"
)


# =====================================================
# DIRECTORIES
# =====================================================

BASE_DIR = Path(__file__).resolve().parent

UPLOAD_DIR = BASE_DIR / "storage" / "uploads"

OUTPUT_DIR = BASE_DIR / "storage" / "outputs"

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =====================================================
# AI ENGINE
# =====================================================

ai_engine = AIEngine()


# =====================================================
# ALLOWED IMAGE TYPES
# =====================================================

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/jpg",
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
        "version": "2.4.0"
    }


# =====================================================
# HEALTH CHECK
# =====================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",

        "ai_engine": ai_engine.status(),

        "story_intelligence": {
            "engine": story_intelligence.engine_name,
            "version": story_intelligence.version,
            "status": "ready"
        },

        "scene_planner": {
            "engine": scene_planner.engine_name,
            "version": scene_planner.version,
            "status": "ready"
        },

        "continuity_engine": {
            "engine": continuity_engine.engine_name,
            "version": continuity_engine.version,
            "status": "ready"
        }
    }


# =====================================================
# AI ENGINE STATUS
# =====================================================

@app.get("/v1/engine/status")
def engine_status():

    return ai_engine.status()


# =====================================================
# STORY ANALYSIS
# =====================================================

@app.post("/v1/story/analyze")
def analyze_story(
    story: str = Form(...)
):

    try:

        analysis = (
            story_intelligence.analyze_story(
                story
            )
        )

        return {
            "success": True,
            "analysis": analysis
        }

    except Exception as error:

        logger.exception(
            "Story analysis failed"
        )

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# =====================================================
# STORY PLAN
# =====================================================

@app.post("/v1/story/plan")
def plan_story(
    story: str = Form(...)
):

    try:

        story_analysis = (
            story_intelligence.analyze_story(
                story
            )
        )

        scene_plan = (
            scene_planner.create_scene_plan(
                story_analysis
            )
        )

        return {
            "success": True,
            "story_analysis": story_analysis,
            "scene_plan": scene_plan
        }

    except Exception as error:

        logger.exception(
            "Story planning failed"
        )

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# =====================================================
# FULL STORY PLAN
# =====================================================

@app.post("/v1/story/full-plan")
def create_full_story_plan(
    story: str = Form(...)
):

    try:

        story_analysis = (
            story_intelligence.analyze_story(
                story
            )
        )

        scene_plan = (
            scene_planner.create_scene_plan(
                story_analysis
            )
        )

        continuity_plan = (
            continuity_engine.build_continuity(
                story_analysis,
                scene_plan
            )
        )

        return {
            "success": True,
            "story_analysis": story_analysis,
            "scene_plan": scene_plan,
            "continuity_plan": continuity_plan
        }

    except Exception as error:

        logger.exception(
            "Full story planning failed"
        )

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# =====================================================
# GET JOB STATUS
# =====================================================

@app.get("/v1/jobs/{job_id}")
def get_job(
    job_id: str
):

    job = job_manager.get_job(
        job_id
    )

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

        logger.info(
            f"Starting video job: {job_id}"
        )

        job_manager.update_status(
            job_id,
            "processing"
        )

        output_file = (
            OUTPUT_DIR /
            f"{job_id}.mp4"
        )

        result = ai_engine.generate(
            image_path=input_file,
            output_path=output_file,
            prompt=prompt,
            mode=mode,
            duration=duration
        )

        if result is None:

            raise RuntimeError(
                "AI provider did not return a video."
            )

        if not result.exists():

            raise RuntimeError(
                "Generated video file was not found."
            )

        if result.stat().st_size <= 0:

            raise RuntimeError(
                "Generated video file is empty."
            )

        video_url = (
            f"/storage/outputs/{job_id}.mp4"
        )

        job_manager.update_status(
            job_id,
            "completed",
            video_url=video_url
        )

        logger.info(
            f"Video job completed: {job_id}"
        )

    except Exception as error:

        logger.exception(
            f"Video job failed: {job_id}"
        )

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
    duration: int = Form(6)
):

    try:

        logger.info(
            "New image-to-video request received"
        )

        logger.info(
            f"Content type: {image.content_type}"
        )

        logger.info(
            f"Filename: {image.filename}"
        )

        logger.info(
            f"Mode: {mode}"
        )

        logger.info(
            f"Duration: {duration}"
        )

        # =============================================
        # VALIDATE IMAGE
        # =============================================

        if image.content_type not in ALLOWED_IMAGE_TYPES:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Only JPEG, PNG and WebP images "
                    "are supported."
                )
            )

        # =============================================
        # VALIDATE DURATION
        # =============================================

        if duration not in [6, 10]:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Supported durations are 6 or 10 seconds."
                )
            )

        # =============================================
        # CREATE JOB
        # =============================================

        job_id = str(
            uuid4()
        )

        logger.info(
            f"Creating job: {job_id}"
        )

        job_manager.create_job(
            job_id=job_id,
            prompt=prompt,
            mode=mode,
            duration=duration
        )

        # =============================================
        # DETERMINE EXTENSION
        # =============================================

        extension = ".jpg"

        if image.content_type == "image/png":

            extension = ".png"

        elif image.content_type == "image/webp":

            extension = ".webp"

        # =============================================
        # SAVE IMAGE
        # =============================================

        input_file = (
            UPLOAD_DIR /
            f"{job_id}{extension}"
        )

        logger.info(
            f"Saving uploaded image: {input_file}"
        )

        try:

            with input_file.open(
                "wb"
            ) as buffer:

                shutil.copyfileobj(
                    image.file,
                    buffer
                )

            if not input_file.exists():

                raise RuntimeError(
                    "Uploaded image file was not created."
                )

            if input_file.stat().st_size <= 0:

                raise RuntimeError(
                    "Uploaded image file is empty."
                )

            logger.info(
                "Image uploaded successfully. "
                f"Size: {input_file.stat().st_size} bytes"
            )

        except Exception as error:

            logger.exception(
                "Image saving failed"
            )

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

        finally:

            try:

                await image.close()

            except Exception:

                pass

        # =============================================
        # ADD BACKGROUND JOB
        # =============================================

        logger.info(
            f"Adding background task: {job_id}"
        )

        background_tasks.add_task(
            process_video_job,
            job_id,
            input_file,
            prompt,
            mode,
            duration
        )

        # =============================================
        # RESPONSE
        # =============================================

        return JSONResponse(
            status_code=200,
            content={
                "success": True,

                "job_id": job_id,

                "status": "queued",

                "message": (
                    "Video job added successfully."
                ),

                "status_url": (
                    f"/v1/jobs/{job_id}"
                )
            }
        )

    except HTTPException:

        raise

    except Exception as error:

        logger.error(
            "IMAGE-TO-VIDEO REQUEST FAILED"
        )

        logger.error(
            traceback.format_exc()
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Server error: {str(error)}"
            )
        )
