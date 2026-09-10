from pathlib import Path
from typing import Optional

from ai_provider import AIProvider


class AIEngine:

    # =====================================================
    # INITIALIZE
    # =====================================================

    def __init__(self):

        self.name = "Story2Video AI Engine"

        self.version = "2.4.0"

        self.provider = AIProvider()


    # =====================================================
    # STATUS
    # =====================================================

    def status(self) -> dict:

        provider_status = self.provider.status()

        return {

            "engine": self.name,

            "version": self.version,

            "connected": provider_status["connected"],

            "supported_durations": [
                6,
                10
            ],

            "default_duration": 6,

            "supported_modes": [
                "AI Motion",
                "Face Motion",
                "Cinematic Motion"
            ],

            "provider": provider_status
        }


    # =====================================================
    # GENERATE VIDEO
    # =====================================================

    def generate(

        self,

        image_path: Path,

        output_path: Path,

        prompt: str = "",

        mode: str = "AI Motion",

        duration: int = 6,

        image_url: Optional[str] = None

    ) -> Optional[Path]:


        # =================================================
        # CHECK INPUT IMAGE
        # =================================================

        if not image_path.exists():

            raise FileNotFoundError(
                "Input image was not found."
            )


        # =================================================
        # CHECK PUBLIC IMAGE URL
        # =================================================

        if not image_url:

            raise ValueError(
                "Public image URL is missing."
            )


        if not image_url.startswith("http"):

            raise ValueError(
                "Public image URL is invalid."
            )


        # =================================================
        # CHECK DURATION
        # =================================================

        supported_durations = {
            6,
            10
        }


        if duration not in supported_durations:

            raise ValueError(
                "Supported video durations are "
                "6 or 10 seconds."
            )


        # =================================================
        # CHECK MODE
        # =================================================

        allowed_modes = {

            "AI Motion",

            "Face Motion",

            "Cinematic Motion"

        }


        if mode not in allowed_modes:

            raise ValueError(
                f"Unsupported animation mode: {mode}"
            )


        # =================================================
        # CREATE OUTPUT DIRECTORY
        # =================================================

        output_path.parent.mkdir(

            parents=True,

            exist_ok=True
        )


        # =================================================
        # SEND TO AI PROVIDER
        # =================================================

        result = self.provider.generate_video(

            image_path=image_path,

            output_path=output_path,

            prompt=prompt,

            mode=mode,

            duration=duration,

            image_url=image_url
        )


        # =================================================
        # CHECK RESULT
        # =================================================

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


        return result
