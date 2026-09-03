
from pathlib import Path
from typing import Optional
import shutil


class AIEngine:
    """
    Story2Video AI Animation Engine

    এই class-এর কাজ:
    - input image গ্রহণ করা
    - prompt গ্রহণ করা
    - 10-second video generation-এর জন্য
      ভবিষ্যতের AI model-কে call করার জায়গা তৈরি রাখা

    বর্তমানে এটি model-এর placeholder।
    আসল image-to-video model পরের ধাপে যুক্ত হবে।
    """

    def __init__(self):
        self.name = "Story2Video AI Engine"
        self.version = "1.0.0"
        self.connected = False

    def status(self) -> dict:
        return {
            "engine": self.name,
            "version": self.version,
            "connected": self.connected,
            "duration": 10,
            "supported_modes": [
                "AI Motion",
                "Face Motion",
                "Cinematic Motion"
            ]
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
                "Story2Video supports only 10-second videos."
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

        # --------------------------------------------------
        # IMPORTANT
        # --------------------------------------------------
        # এখানে পরের ধাপে আসল AI image-to-video model
        # যুক্ত করা হবে।
        #
        # এখনো কোনো fake video তৈরি করা হচ্ছে না।
        # --------------------------------------------------

        raise RuntimeError(
            "AI video model is not connected yet. "
            "The Story2Video AI engine is ready for "
            "model integration."
        )
