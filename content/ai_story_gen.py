"""
AI Content Factory - AI Story Generator
Generates engaging multi-act stories, character lore, and storyboards.
"""

from typing import Dict, Any, Optional

from content.script_generator import ScriptGenerator
from utils.helpers import logger


class AIStoryGenerator:
    """Generates creative stories and character-driven episodic narratives."""

    GENRES = {
        "cartoon": "humorous, colorful, animated adventure with expressive animal or human heroes",
        "mystery": "suspenseful, thrilling investigative mystery with unexpected twists and clues",
        "scifi": "epic futuristic science fiction with advanced AI, interstellar travel, and dystopian mysteries",
        "horror": "creepy, eerie urban legend / psychological horror with building dread and chills",
        "fable": "heartwarming folk tale with a profound moral lesson for all ages"
    }

    def __init__(self):
        self.script_gen = ScriptGenerator()

    def generate_story(
        self,
        premise: str,
        genre: str = "cartoon",
        target_length: str = "60s",
        main_character: Optional[str] = None
    ) -> Dict[str, Any]:
        genre_desc = self.GENRES.get(genre.lower(), self.GENRES["cartoon"])
        char_prompt = f" featuring main character: {main_character}" if main_character else ""
        topic_prompt = f"Genre: {genre} ({genre_desc}). Story premise: {premise}{char_prompt}"

        logger.info(f"Generating story for genre '{genre}': {premise[:40]}...")

        content_type = "cartoon_series" if genre == "cartoon" else "mystery"
        story_script = self.script_gen.generate_script(
            topic=topic_prompt,
            content_type=content_type,
            target_duration=target_length,
            tone="cinematic and immersive"
        )

        return {
            "title": story_script.get("title", f"The Tale of {premise[:30]}"),
            "genre": genre,
            "premise": premise,
            "main_character": main_character or "Protagonist",
            "full_story_text": story_script.get("full_voiceover_text", ""),
            "scenes": story_script.get("scenes", []),
            "estimated_duration_seconds": story_script.get("estimated_duration_seconds", 60)
        }
