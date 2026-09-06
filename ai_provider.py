from pathlib import Path
from typing import Optional
import os


class AIProvider:
    """
    Story2Video AI Model Provider

    এই Provider-এর কাজ হলো:
    AIEngine এবং ভবিষ্যতের GPU Video Model-এর
    মধ্যে connection তৈরি করা।
    """

    def __init__(self):
        self.provider_name = "Story2Video GPU Provider"

        # ভবিষ্যতে GPU Server URL এখানে থাকবে
        self.gpu_server_url = os.getenv(
            "GPU_SERVER_URL",
            ""
        )

        self.api_key = os.getenv(
            "GPU_SERVER_API_KEY",
            ""
        )

    def is_connected(self) -> bool:

        return bool(self.gpu_server_url)

    def status(self) -> dict:

        return {
            "provider": self.provider_name,
            "connected": self.is_connected(),
            "gpu_server_configured": bool(
                self.gpu_server_url
            )
        }

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

        # =================================================
        # GPU MODEL CONNECTION
        # =================================================
        #
        # পরের ধাপে এখানে আমাদের GPU Server API call হবে।
        #
        # GPU Server image গ্রহণ করবে
        # → AI model চালাবে
        # → video তৈরি করবে
        # → video URL/File ফেরত দেবে
        #
        # =================================================

        if not self.is_connected():

            raise RuntimeError(
                "GPU AI Server is not connected yet. "
                "Configure GPU_SERVER_URL first."
            )

        raise RuntimeError(
            "GPU Provider is configured but the "
            "video model connector is not implemented yet."
        )
