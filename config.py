"""
AI Content Factory - Central Configuration Module
Handles environment variables, Streamlit Secrets, and default paths.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory Paths
ROOT_DIR = Path(__file__).parent.resolve()
OUTPUT_DIR = ROOT_DIR / "output"
TEMP_DIR = ROOT_DIR / "temp"
ASSETS_DIR = ROOT_DIR / "assets"
MUSIC_DIR = ASSETS_DIR / "music"
FONTS_DIR = ASSETS_DIR / "fonts"

# Load environment variables from .env if present
load_dotenv(ROOT_DIR / ".env")

# Ensure all vital directories exist
for path in [OUTPUT_DIR, TEMP_DIR, ASSETS_DIR, MUSIC_DIR, FONTS_DIR]:
    path.mkdir(parents=True, exist_ok=True)


def get_secret(key: str, default: str = "") -> str:
    """Helper to fetch secrets from Streamlit secrets (Cloud) or environment variables (Local/CLI)."""
    val = os.getenv(key)
    if val:
        return val.strip()

    # Check Streamlit Cloud st.secrets if available
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            return str(st.secrets[key]).strip()
    except Exception:
        pass

    return default


# API Keys and Models
GROQ_API_KEY = get_secret("GROQ_API_KEY", "")
GROQ_MODEL = get_secret("GROQ_MODEL", "llama3-70b-8192")

GEMINI_API_KEY = get_secret("GEMINI_API_KEY", "")
GEMINI_MODEL = get_secret("GEMINI_MODEL", "gemini-1.5-flash")

DEFAULT_LLM_PROVIDER = get_secret("DEFAULT_LLM_PROVIDER", "groq").lower()

PEXELS_API_KEY = get_secret("PEXELS_API_KEY", "")

# Voiceover Settings (100% Free Edge-TTS)
DEFAULT_VOICE = get_secret("DEFAULT_VOICE", "en-US-GuyNeural")
DEFAULT_VOICE_RATE = get_secret("DEFAULT_VOICE_RATE", "+0%")
DEFAULT_VOICE_PITCH = get_secret("DEFAULT_VOICE_PITCH", "+0Hz")

AVAILABLE_VOICES = {
    "US Male (Guy - Deep & Energetic)": "en-US-GuyNeural",
    "US Female (Jenny - Natural & Expressive)": "en-US-JennyNeural",
    "US Male (Christopher - Documentary/Story)": "en-US-ChristopherNeural",
    "US Female (Aria - Professional/News)": "en-US-AriaNeural",
    "US Male (Eric - Casual & Friendly)": "en-US-EricNeural",
    "UK Female (Sonia - Eloquent/Refined)": "en-GB-SoniaNeural",
    "UK Male (Ryan - Dynamic/Engaging)": "en-GB-RyanNeural",
    "AU Female (Natasha - Warm/Bright)": "en-AU-NatashaNeural",
    "IN Male (Prabhat - Informative)": "en-IN-PrabhatNeural",
    "ES Male (Alvaro - Spanish)": "es-ES-AlvaroNeural",
    "FR Male (Henri - French)": "fr-FR-HenriNeural",
    "DE Male (Conrad - German)": "de-DE-ConradNeural",
}

# Video Resolution Dimensions (Width, Height)
RESOLUTION_MAP = {
    "landscape": {
        "1080p": (1920, 1080),
        "720p": (1280, 720),
        "4k": (3840, 2160)
    },
    "vertical": { # Shorts / TikTok / Reels
        "1080p": (1080, 1920),
        "720p": (720, 1280),
        "4k": (2160, 3840)
    },
    "square": { # Instagram Post
        "1080p": (1080, 1080),
        "720p": (720, 720)
    }
}

DEFAULT_RESOLUTION = get_secret("VIDEO_RESOLUTION", "1080p")
DEFAULT_ORIENTATION = get_secret("VIDEO_ORIENTATION", "landscape")

# Platform Integration Credentials
YOUTUBE_CLIENT_SECRETS_FILE = get_secret("YOUTUBE_CLIENT_SECRETS_FILE", str(ROOT_DIR / "client_secrets.json"))
YOUTUBE_TOKEN_FILE = get_secret("YOUTUBE_TOKEN_FILE", str(ROOT_DIR / "token.json"))

FACEBOOK_PAGE_ACCESS_TOKEN = get_secret("FACEBOOK_PAGE_ACCESS_TOKEN", "")
FACEBOOK_PAGE_ID = get_secret("FACEBOOK_PAGE_ID", "")

# Scheduler
AUTO_SCHEDULE_INTERVAL_HOURS = int(get_secret("AUTO_SCHEDULE_INTERVAL_HOURS", "24"))
AUTO_POST_NICHE = get_secret("AUTO_POST_NICHE", "tech")
