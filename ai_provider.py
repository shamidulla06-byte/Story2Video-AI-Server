import os
import shutil

from pathlib import Path
from typing import Optional

import requests

from config import settings


class AIProvider:

    # =================================================
    # INITIALIZE
    # =================================================

    def __init__(self):

        self.provider_name = (
            settings.AI_PROVIDER
        )

        self.fal_key = (
            settings.FAL_KEY.strip()
            if settings.FAL_KEY
            else ""
        )

        self.fal_model = (
            settings.FAL_MODEL
        )

        self.gpu_server_url = (
            settings.GPU_SERVER_URL
        )

        self.gpu_api_key = (
            settings.GPU_SERVER_API_KEY
        )

        self.huggingface_api_key = (
            settings.HUGGINGFACE_API_KEY
        )

        # Make key available to fal-client

        if self.fal_key:

            os.environ["FAL_KEY"] = (
                self.fal_key
            )


    # =================================================
    # CONNECTION CHECK
    # =================================================

    def is_connected(self) -> bool:

        if self.provider_name == "fal":

            return bool(self.fal_key)

        if self.provider_name == "local":

            return False

        if self.provider_name == "gpu_server":

            return bool(
                self.gpu_server_url
            )

        if self.provider_name == "huggingface":

            return bool(
                self.huggingface_api_key
            )

        return False


    # =================================================
    # STATUS
    # =================================================

    def status(self) -> dict:

        return {

            "provider":
                self.provider_name,

            "connected":
                self.is_connected(),

            "fal_configured":
                bool(self.fal_key),

            "fal_model":
                self.fal_model,

            "gpu_server_configured":
                bool(self.gpu_server_url),

            "huggingface_configured":
                bool(
                    self.huggingface_api_key
                ),

            "available_providers": [

                "fal",

                "local",

                "huggingface",

                "gpu_server"
            ]
        }


    # =================================================
    # GET FAL CLIENT
    # =================================================

    def get_fal_client(self):

        if not self.fal_key:

            raise RuntimeError(
                "FAL_KEY is not configured."
            )

        os.environ["FAL_KEY"] = (
            self.fal_key
        )

        try:

            import fal_client

            return fal_client

        except ImportError:

            raise RuntimeError(
                "fal-client package "
                "is not installed."
            )


    # =================================================
    # DOWNLOAD VIDEO
    # =================================================

    def download_video(

        self,

        video_url: str,

        output_path: Path

    ) -> Path:


        output_path.parent.mkdir(

            parents=True,

            exist_ok=True
        )


        try:

            response = requests.get(

                video_url,

                stream=True,

                timeout=300
            )


            response.raise_for_status()


            with output_path.open(
                "wb"
            ) as video_file:


                shutil.copyfileobj(

                    response.raw,

                    video_file
                )


        except Exception as error:


            raise RuntimeError(

                "Video download failed: "

                f"{str(error)}"
            )


        if not output_path.exists():

            raise RuntimeError(

                "Video file was not created."
            )


        if output_path.stat().st_size <= 0:

            raise RuntimeError(

                "Downloaded video is empty."
            )


        return output_path


    # =================================================
    # BUILD PROMPT
    # =================================================

    def build_prompt(

        self,

        prompt: str,

        mode: str

    ) -> str:


        mode_instruction = {


            "AI Motion":

                "Create smooth, realistic and "
                "natural subject movement.",


            "Face Motion":

                "Create subtle realistic facial "
                "expressions and natural movement "
                "while preserving identity.",


            "Cinematic Motion":

                "Create cinematic camera movement, "
                "smooth motion and realistic depth."

        }.get(

            mode,

            "Create smooth realistic motion."
        )


        return (

            f"{prompt}\n\n"

            f"{mode_instruction}\n\n"

            "Preserve the original person's identity. "
            "Maintain character consistency. "
            "Do not distort the face. "
            "Keep the image visually coherent. "
            "High quality realistic animation."
        )


    # =================================================
    # EXTRACT VIDEO URL
    # =================================================

    def extract_video_url(

        self,

        result

    ) -> str:


        if not isinstance(result, dict):

            raise RuntimeError(

                "Unexpected FAL response format."
            )


        video_data = result.get(
            "video"
        )


        if isinstance(video_data, dict):

            video_url = (
                video_data.get("url")
            )

            if video_url:

                return video_url


        # Some models may return videos array

        videos = result.get(
            "videos"
        )


        if isinstance(videos, list):

            if len(videos) > 0:

                first_video = videos[0]

                if isinstance(first_video, dict):

                    video_url = (
                        first_video.get("url")
                    )

                    if video_url:

                        return video_url


        raise RuntimeError(

            "FAL did not return a video URL. "
            f"Response: {result}"
        )


    # =================================================
    # GENERATE VIDEO
    # =================================================

    def generate_video(

        self,

        image_path: Path,

        output_path: Path,

        prompt: str,

        mode: str,

        duration: int,

        image_url: Optional[str] = None

    ) -> Optional[Path]:


        if not image_path.exists():

            raise FileNotFoundError(

                "Input image was not found."
            )


        # =============================================
        # FAL
        # =============================================

        if self.provider_name == "fal":


            if not self.fal_key:

                raise RuntimeError(

                    "FAL_KEY is not configured."
                )


            # IMPORTANT:
            # We do NOT upload to fal storage.


            if not image_url:

                raise RuntimeError(

                    "Public image URL is missing."
                )


            if not image_url.startswith(
                "http"
            ):

                raise RuntimeError(

                    "Image URL must be public."
                )


            fal_client = (
                self.get_fal_client()
            )


            final_prompt = (
                self.build_prompt(
                    prompt,
                    mode
                )
            )


            # =========================================
            # CALL FAL MODEL USING PUBLIC URL
            # =========================================

            try:


                result = (
                    fal_client.subscribe(

                        self.fal_model,

                        arguments={

                            "prompt":
                                final_prompt,

                            "image_url":
                                image_url,

                            "duration":
                                duration
                        }
                    )
                )


            except Exception as error:


                raise RuntimeError(

                    "FAL video generation failed: "

                    f"{str(error)}"
                )


            # =========================================
            # VIDEO URL
            # =========================================

            video_url = (
                self.extract_video_url(
                    result
                )
            )


            # =========================================
            # DOWNLOAD
            # =========================================

            return self.download_video(

                video_url,

                output_path
            )


        # =============================================
        # LOCAL
        # =============================================

        if self.provider_name == "local":

            raise RuntimeError(

                "No local AI provider "
                "is connected."
            )


        # =============================================
        # HUGGINGFACE
        # =============================================

        if self.provider_name == "huggingface":

            raise RuntimeError(

                "HuggingFace provider "
                "is not implemented yet."
            )


        # =============================================
        # GPU SERVER
        # =============================================

        if self.provider_name == "gpu_server":

            raise RuntimeError(

                "GPU server provider "
                "is not implemented yet."
            )


        raise RuntimeError(

            f"Unknown AI provider: "

            f"{self.provider_name}"
        )


# =====================================================
# GLOBAL PROVIDER
# =====================================================

ai_provider = AIProvider()
