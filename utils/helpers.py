"""
AI Content Factory - Helpers and Utility Functions
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("ai_content_factory")


def sanitize_filename(name: str, max_length: int = 60) -> str:
    """Sanitizes a string to be safely used as a filename."""
    clean = re.sub(r'[\\/*?:"<>|]', "", name)
    clean = re.sub(r"[\s_]+", "_", clean).strip("_")
    clean = clean.encode("ascii", "ignore").decode("ascii")
    if not clean:
        clean = "content_item"
    return clean[:max_length]


def save_json(data: Any, filepath: Path) -> bool:
    """Safely saves a python dictionary or list as formatted JSON."""
    try:
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON to {filepath}: {e}")
        return False


def load_json(filepath: Path, default: Optional[Any] = None) -> Any:
    """Safely loads a JSON file with fallback default."""
    try:
        filepath = Path(filepath)
        if not filepath.exists():
            return default if default is not None else {}
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON from {filepath}: {e}")
        return default if default is not None else {}


def format_duration(seconds: float) -> str:
    """Formats duration in seconds to MM:SS format."""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"
