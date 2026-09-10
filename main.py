from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    HTTPException,
    BackgroundTasks,
    Request
)

from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from pathlib import Path
from uuid import uuid4
import shutil

from ai_engine import AIEngine
from job_manager import job_manager
from story_intelligence import story_intelligence
from scene_planner import scene_planner
from continuity_engine import continuity_engine


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

STORAGE_DIR = BASE_DIR / "storage"

UPLOAD_DIR = STORAGE_DIR / "uploads"

OUTPUT_DIR = STORAGE_DIR / "outputs"


UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =====================================================
# PUBLIC STORAGE
# =====================================================

app.mount(
    "/storage",
    StaticFiles(directory=str(STORAGE_DIR)),
    name="storage"
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
# HEALTH
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
# ENGINE STATUS
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

    except ValueError as error:

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

    except ValueError as error:

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

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# =====================================================
# GET JOB
# =====================================================

@app.get("/v1/jobs/{job_id}")
def get_job(
    job_id: str
):

    job = job_manager.get_job(job_id)

    if job is None:

        raise HTTPException(
            status_code=404,
            detail="Job not found."
        )

    return job


# =====================================================
# PROCESS VIDEO JOB
# =====================================================

def process_video_job(
    job_id: str,
    input_file: Path,
    image_url: str,
    prompt: str,
    mode: str,
    duration: int
):

    try:

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

            duration=duration,

            image_url=image_url
        )

        if result is None:

            raise RuntimeError(
                "AI provider did not return a video."
            )

        video_url = (
            f"/storage/outputs/{job_id}.mp4"
        )

        job_manager.update_status(

            job_id,

            "completed",

            video_url=video_url
        )

    except Exception as error:

        job_manager.update_status(

            job_id,

            "failed",

            error=str(error)
        )


# =====================================================
# IMAGE TO VIDEO
# =====================================================

@app.post("/v1/image-to-video")
async def image_to_video(

    request: Request,

    background_tasks: BackgroundTasks,

    image: UploadFile = File(...),

    prompt: str = Form(""),

    mode: str = Form("AI Motion"),

    duration: int = Form(6)
):


    # =================================================
    # VALIDATE IMAGE
    # =================================================

    if image.content_type not in ALLOWED_IMAGE_TYPES:

        raise HTTPException(

            status_code=400,

            detail=(
                "Only JPEG, PNG and WebP images "
                "are supported."
            )
        )


    # =================================================
    # VALIDATE DURATION
    # =================================================

    if duration not in [6, 10]:

        raise HTTPException(

            status_code=400,

            detail=(
                "Supported durations are "
                "6 or 10 seconds."
            )
        )


    # =================================================
    # CREATE JOB
    # =================================================

    job_id = str(uuid4())


    job_manager.create_job(

        job_id=job_id,

        prompt=prompt,

        mode=mode,

        duration=duration
    )


    # =================================================
    # FILE EXTENSION
    # =================================================

    extension = ".jpg"


    if image.content_type == "image/png":

        extension = ".png"


    elif image.content_type == "image/webp":

        extension = ".webp"


    # =================================================
    # SAVE IMAGE
    # =================================================

    input_file = (

        UPLOAD_DIR /

        f"{job_id}{extension}"
    )


    try:

        with input_file.open(
            "wb"
        ) as buffer:

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


    # =================================================
    # CREATE PUBLIC IMAGE URL
    # =================================================

    base_url = str(
        request.base_url
    ).rstrip("/")


    image_url = (

        f"{base_url}"

        f"/storage/uploads/"

        f"{job_id}{extension}"
    )


    # =================================================
    # START BACKGROUND JOB
    # =================================================

    background_tasks.add_task(

        process_video_job,

        job_id,

        input_file,

        image_url,

        prompt,

        mode,

        duration
    )


    # =================================================
    # RESPONSE
    # =================================================

    return JSONResponse(

        content={

            "success": True,

            "job_id": job_id,

            "status": "queued",

            "image_url": image_url,

            "message":

                "Video job added to queue.",

            "status_url":

                f"/v1/jobs/{job_id}"
        }
    )
