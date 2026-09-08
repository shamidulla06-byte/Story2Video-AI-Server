from pathlib import Path
from typing import Optional
import os

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

            raise RuntimeError(
                "FAL provider connection is ready, "
                "but the API request connector "
                "will be added in the next step."
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
