import os


class Settings:
    """
    Story2Video Configuration

    সমস্ত গুরুত্বপূর্ণ configuration এক জায়গায় রাখা হয়েছে।
    Secret/API key কখনো source code-এর মধ্যে লেখা হবে না।
    """

    APP_NAME = "Story2Video AI Server"
    APP_VERSION = "2.0.0"

    # -----------------------------------------
    # AI PROVIDER
    # -----------------------------------------

    AI_PROVIDER = os.getenv(
        "AI_PROVIDER",
        "local"
    )

    # -----------------------------------------
    # GPU SERVER
    # -----------------------------------------

    GPU_SERVER_URL = os.getenv(
        "GPU_SERVER_URL",
        ""
    )

    GPU_SERVER_API_KEY = os.getenv(
        "GPU_SERVER_API_KEY",
        ""
    )

    # -----------------------------------------
    # HUGGING FACE
    # -----------------------------------------

    HUGGINGFACE_API_KEY = os.getenv(
        "HUGGINGFACE_API_KEY",
        ""
    )

    # -----------------------------------------
    # VIDEO SETTINGS
    # -----------------------------------------

    VIDEO_DURATION = 10

    SUPPORTED_MODES = [
        "AI Motion",
        "Face Motion",
        "Cinematic Motion"
    ]


settings = Settings()
