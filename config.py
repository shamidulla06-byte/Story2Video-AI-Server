import os


class Settings:
    """
    Story2Video AI Server Configuration
    """

    # =========================================
    # APPLICATION
    # =========================================

    APP_NAME = "Story2Video AI Server"
    APP_VERSION = "2.4.0"

    # =========================================
    # AI PROVIDER
    # =========================================

    AI_PROVIDER = os.getenv(
        "AI_PROVIDER",
        "fal"
    )

    # =========================================
    # FAL AI CONFIGURATION
    # =========================================

    FAL_KEY = os.getenv(
        "FAL_KEY",
        ""
    )

    FAL_MODEL = os.getenv(
        "FAL_MODEL",
        "wan/v2.6/image-to-video"
    )

    # =========================================
    # GPU SERVER
    # =========================================

    GPU_SERVER_URL = os.getenv(
        "GPU_SERVER_URL",
        ""
    )

    GPU_SERVER_API_KEY = os.getenv(
        "GPU_SERVER_API_KEY",
        ""
    )

    # =========================================
    # HUGGING FACE
    # =========================================

    HUGGINGFACE_API_KEY = os.getenv(
        "HUGGINGFACE_API_KEY",
        ""
    )

    # =========================================
    # VIDEO SETTINGS
    # =========================================

    VIDEO_DURATION = 10

    SUPPORTED_MODES = [
        "AI Motion",
        "Face Motion",
        "Cinematic Motion"
    ]


settings = Settings()
