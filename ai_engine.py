from pathlib import Path
from typing import Optional

from ai_provider import AIProvider


class AIEngine:

    def __init__(self):

        self.name = "Story2Video AI Engine"

        self.version = "2.0.0"

        self.provider = AIProvider()

    def status(self) -> dict:

        provider_status = self.provider.status()

        return {
            "engine": self.name,
            "version": self.version,
            "connected": provider_status["connected"],
            "duration": 10,
            "supported_modes": [
                "AI Motion",
                "Face Motion",
                "Cinematic Motion"
            ],
            "provider": provider_status
        }

    def generate(
        self,
        image_path: Path,
        output_path: Path,
        prompt: str = "",
        mode: str = "AI Motion",
        duration: int = 10
    ) -> Optional[Path]:

        if not image_path.exists():

            raise FileNotFoundError(
                "Input image was not found."
            )

        if duration != 10:

            raise ValueError(
                "Currently only 10-second videos "
                "are supported."
            )

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
        # SEND TO OUR AI PROVIDER
        # =================================================

        return self.provider.generate_video(
            image_path=image_path,
            output_path=output_path,
            prompt=prompt,
            mode=mode,
            duration=duration
        )
