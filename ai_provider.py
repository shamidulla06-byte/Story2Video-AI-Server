from pathlib import Path
from typing import Optional
import shutil
import requests

from config import settings


class AIProvider:

    def __init__(self):

        self.provider_name = settings.AI_PROVIDER

        self.fal_key = settings.FAL_KEY
        self.fal_model = settings.FAL_MODEL

        self.gpu_server_url = (
            settings.GPU_SERVER_URL
        )

        self.gpu_api_key = (
            settings.GPU_SERVER_API_KEY
        )

        self.huggingface_api_key = (
            settings.HUGGINGFACE_API_KEY
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
            return bool(self.gpu_server_url)

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
            "provider": self.provider_name,

            "connected": self.is_connected(),

            "fal_configured": bool(
                self.fal_key
            ),

            "fal_model": self.fal_model,

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
    # FAL IMAGE UPLOAD
    # =========================================

    def upload_image_to_fal(
        self,
        image_path: Path
    ) -> str:

        try:

            import fal_client

        except ImportError:

            raise RuntimeError(
                "fal-client package is not installed."
            )

        uploaded_url = (
            fal_client.upload_file(
                str(image_path)
            )
        )

        return uploaded_url

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

        response = requests.get(
            video_url,
            stream=True,
            timeout=300
        )

        response.raise_for_status()

        with output_path.open("wb") as video_file:

            shutil.copyfileobj(
                response.raw,
                video_file
            )

        return output_path

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
                    "FAL_KEY is not configured."
                )

            try:

                import fal_client

            except ImportError:

                raise RuntimeError(
                    "fal-client package is not installed."
                )

            # ---------------------------------
            # UPLOAD IMAGE TO FAL STORAGE
            # ---------------------------------

            image_url = (
                self.upload_image_to_fal(
                    image_path
                )
            )

            # ---------------------------------
            # BUILD VIDEO PROMPT
            # ---------------------------------

            final_prompt = (
                f"{prompt}\n\n"
                f"Animation mode: {mode}. "
                "Maintain character identity and "
                "visual consistency. Natural motion. "
                "Cinematic quality."
            )

            # ---------------------------------
            # CALL FAL MODEL
            # ---------------------------------

            result = fal_client.subscribe(
                self.fal_model,
                arguments={
                    "prompt": final_prompt,
                    "image_url": image_url,
                    "duration": duration
                }
            )

            # ---------------------------------
            # GET VIDEO URL
            # ---------------------------------

            video_data = result.get(
                "video"
            )

            if not video_data:

                raise RuntimeError(
                    "FAL did not return video data."
                )

            video_url = video_data.get(
                "url"
            )

            if not video_url:

                raise RuntimeError(
                    "FAL did not return a video URL."
                )

            # ---------------------------------
            # DOWNLOAD FINAL VIDEO
            # ---------------------------------

            return self.download_video(
                video_url,
                output_path
            )

        # =====================================
        # LOCAL
        # =====================================

        if self.provider_name == "local":

            raise RuntimeError(
                "No AI provider is connected yet."
            )

        # =====================================
        # HUGGINGFACE
        # =====================================

        if self.provider_name == "huggingface":

            raise RuntimeError(
                "Hugging Face provider connector "
                "is not implemented yet."
            )

        # =====================================
        # GPU SERVER
        # =====================================

        if self.provider_name == "gpu_server":

            raise RuntimeError(
                "GPU server connector "
                "is not implemented yet."
            )

        raise RuntimeError(
            f"Unknown AI provider: "
            f"{self.provider_name}"
        )


ai_provider = AIProvider()
