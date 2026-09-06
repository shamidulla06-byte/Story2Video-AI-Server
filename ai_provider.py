from pathlib import Path
from typing import Optional

from config import settings


class AIProvider:
    """
    Story2Video AI Provider

    এই class বিভিন্ন AI Video Provider-এর
    configuration এবং connection পরিচালনা করে।

    বর্তমানে supported architecture:

    - local
    - huggingface
    - gpu_server

    ভবিষ্যতে নতুন provider সহজে যোগ করা যাবে।
    """

    def __init__(self):

        self.provider_name = settings.AI_PROVIDER

        self.gpu_server_url = (
            settings.GPU_SERVER_URL
        )

        self.gpu_api_key = (
            settings.GPU_SERVER_API_KEY
        )

        self.huggingface_api_key = (
            settings.HUGGINGFACE_API_KEY
        )

    # -----------------------------------------
    # CONNECTION CHECK
    # -----------------------------------------

    def is_connected(self) -> bool:

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

    # -----------------------------------------
    # PROVIDER STATUS
    # -----------------------------------------

    def status(self) -> dict:

        return {
            "provider": self.provider_name,
            "connected": self.is_connected(),

            "gpu_server_configured": bool(
                self.gpu_server_url
            ),

            "huggingface_configured": bool(
                self.huggingface_api_key
            ),

            "available_providers": [
                "local",
                "huggingface",
                "gpu_server"
            ]
        }

    # -----------------------------------------
    # VIDEO GENERATION
    # -----------------------------------------

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

        if self.provider_name == "local":

            raise RuntimeError(
                "No AI provider is connected yet."
            )

        if self.provider_name == "huggingface":

            raise RuntimeError(
                "Hugging Face provider connector "
                "is not implemented yet."
            )

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
