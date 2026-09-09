import os
import shutil

from pathlib import Path
from typing import Optional

import requests

from config import settings


class AIProvider:

    # =========================================
    # INITIALIZE
    # =========================================

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

        # =====================================
        # SET FAL KEY BEFORE IMPORTING CLIENT
        # =====================================

        if self.fal_key:

            os.environ["FAL_KEY"] = (
                self.fal_key
            )

    # =========================================
    # CONNECTION CHECK
    # =========================================

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

    # =========================================
    # PROVIDER STATUS
    # =========================================

    def status(self) -> dict:

        return {

            "provider": (
                self.provider_name
            ),

            "connected": (
                self.is_connected()
            ),

            "fal_configured": bool(
                self.fal_key
            ),

            "fal_model": (
                self.fal_model
            ),

            "gpu_server_configured": bool(
                self.gpu_server_url
            ),

            "huggingface_configured": bool(
                self.huggingface_api_key
            ),

            "available_providers": [

                "fal",

                "local",

                "huggingface",

                "gpu_server"
            ]
        }

    # =========================================
    # CHECK FAL API KEY
    # =========================================

    def check_fal_connection(self):

        if not self.fal_key:

            raise RuntimeError(
                "FAL_KEY is not configured."
            )

        headers = {

            "Authorization":
                f"Key {self.fal_key}"

        }

        try:

            response = requests.get(
                "https://api.fal.ai/v1/models",
                headers=headers,
                params={
                    "limit": 1
                },
                timeout=30
            )

            if response.status_code == 401:

                raise RuntimeError(
                    "FAL API key is invalid "
                    "or has been revoked."
                )

            if response.status_code == 403:

                raise RuntimeError(
                    "FAL API key permission "
                    "was denied. Check the key scope."
                )

            response.raise_for_status()

        except requests.RequestException as error:

            raise RuntimeError(
                "FAL authentication check failed: "
                f"{str(error)}"
            )

    # =========================================
    # IMPORT FAL CLIENT
    # =========================================

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
                "fal-client package is not installed."
            )

    # =========================================
    # UPLOAD IMAGE TO FAL
    # =========================================

    def upload_image_to_fal(
        self,
        image_path: Path
    ) -> str:

        if not image_path.exists():

            raise FileNotFoundError(
                "Image file was not found."
            )

        # First verify API authentication

        self.check_fal_connection()

        fal_client = (
            self.get_fal_client()
        )

        try:

            uploaded_url = (
                fal_client.upload_file(
                    str(image_path)
                )
            )

            if not uploaded_url:

                raise RuntimeError(
                    "FAL returned an empty image URL."
                )

            return uploaded_url

        except Exception as error:

            raise RuntimeError(
                "FAL image upload failed: "
                f"{str(error)}"
            )

    # =========================================
    # DOWNLOAD VIDEO
    # =========================================

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
                "Downloaded video file was not created."
            )

        if output_path.stat().st_size <= 0:

            raise RuntimeError(
                "Downloaded video file is empty."
            )

        return output_path

    # =========================================
    # BUILD PROMPT
    # =========================================

    def build_prompt(
        self,
        prompt: str,
        mode: str
    ) -> str:

        mode_instruction = {

            "AI Motion":
                "Create smooth natural realistic "
                "subject motion.",

            "Face Motion":
                "Create subtle natural facial movement "
                "while preserving identity.",

            "Cinematic Motion":
                "Create smooth cinematic camera movement "
                "and realistic motion."

        }.get(
            mode,
            "Create natural realistic motion."
        )

        return (
            f"{prompt}\n\n"
            f"{mode_instruction}\n\n"
            "Maintain character identity. "
            "Maintain visual consistency. "
            "Avoid distortion. "
            "High quality realistic animation."
        )

    # =========================================
    # VIDEO GENERATION
    # =========================================

    def generate_video(
        self,
        image_path: Path,
        output_path: Path,
        prompt: str,
        mode: str,
        duration: int
    ) -> Optional[Path]:

        if not image_path.exists():

            raise FileNotFoundError(
                "Input image was not found."
            )

        # =====================================
        # FAL PROVIDER
        # =====================================

        if self.provider_name == "fal":

            if not self.fal_key:

                raise RuntimeError(
                    "FAL_KEY is not configured "
                    "in Render Environment Variables."
                )

            # Verify key first

            self.check_fal_connection()

            fal_client = (
                self.get_fal_client()
            )

            # =================================
            # UPLOAD IMAGE
            # =================================

            image_url = (
                self.upload_image_to_fal(
                    image_path
                )
            )

            # =================================
            # BUILD PROMPT
            # =================================

            final_prompt = (
                self.build_prompt(
                    prompt,
                    mode
                )
            )

            # =================================
            # CALL AI MODEL
            # =================================

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

            # =================================
            # GET VIDEO DATA
            # =================================

            video_data = result.get(
                "video"
            )

            if not video_data:

                raise RuntimeError(
                    "FAL did not return video data. "
                    f"Response: {result}"
                )

            video_url = video_data.get(
                "url"
            )

            if not video_url:

                raise RuntimeError(
                    "FAL did not return a video URL."
                )

            # =================================
            # DOWNLOAD VIDEO
            # =================================

            return self.download_video(
                video_url,
                output_path
            )

        # =====================================
        # LOCAL
        # =====================================

        if self.provider_name == "local":

            raise RuntimeError(
                "No local AI provider is connected."
            )

        # =====================================
        # HUGGINGFACE
        # =====================================

        if self.provider_name == "huggingface":

            raise RuntimeError(
                "Hugging Face provider is not "
                "implemented yet."
            )

        # =====================================
        # GPU SERVER
        # =====================================

        if self.provider_name == "gpu_server":

            raise RuntimeError(
                "GPU server provider is not "
                "implemented yet."
            )

        raise RuntimeError(
            f"Unknown AI provider: "
            f"{self.provider_name}"
        )


# =========================================
# GLOBAL PROVIDER
# =========================================

ai_provider = AIProvider()
