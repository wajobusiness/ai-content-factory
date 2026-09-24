"""
AI Content Factory - Cartoon Studio
Creates animated cartoon shorts and episodic stories with consistent characters and speech bubbles.
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from PIL import Image, ImageDraw, ImageFont

from config import TEMP_DIR, OUTPUT_DIR
from content.ai_image_gen import AIImageGenerator
from content.ai_story_gen import AIStoryGenerator
from content.voiceover_gen import VoiceoverGenerator
from utils.helpers import logger, sanitize_filename


class CartoonStudio:
    """End-to-end studio for cartoon storytelling, visuals, dialogue, and video generation."""

    def __init__(self):
        self.image_gen = AIImageGenerator()
        self.story_gen = AIStoryGenerator()
        self.voice_gen = VoiceoverGenerator()

    def create_cartoon_episode(
        self,
        premise: str,
        character_name: str = "Robo-Paws the Cyber Pup",
        character_description: str = "an adorable robotic puppy with glowing blue eyes and metallic fur",
        cartoon_style: str = "3d_cartoon",
        voice: str = "en-US-JennyNeural"
    ) -> Dict[str, Any]:
        logger.info(f"Starting Cartoon Studio creation for character '{character_name}'...")

        story = self.story_gen.generate_story(
            premise=f"{premise}. Main Character is {character_name}, {character_description}.",
            genre="cartoon",
            main_character=character_name
        )

        scenes = story.get("scenes", [])
        rendered_scenes = []

        for i, sc in enumerate(scenes):
            raw_prompt = sc.get("visual_prompt") or sc.get("narration") or "cartoon adventure"
            char_prompt = f"{character_name}, {character_description}, {raw_prompt}, 3D Disney Pixar animation render, vibrant daylight, cinematic composition"

            img_path = self.image_gen.generate_image(
                prompt=char_prompt,
                style=cartoon_style,
                width=1280,
                height=720,
                output_filename=f"cartoon_{sanitize_filename(character_name)}_scene_{i+1}"
            )

            on_screen = sc.get("on_screen_text") or sc.get("narration", "")[:35]
            bubble_img_path = self._add_speech_bubble(img_path, on_screen, character_name)

            rendered_scenes.append({
                "scene_number": i + 1,
                "narration": sc.get("narration", ""),
                "image_path": bubble_img_path,
                "duration_seconds": sc.get("duration_seconds", 6)
            })

        full_text = story.get("full_story_text", "")
        voice_result = self.voice_gen.generate(
            text=full_text,
            output_name=f"cartoon_{sanitize_filename(story.get('title', 'episode'))}",
            voice=voice
        )

        return {
            "title": story.get("title", f"The Adventures of {character_name}"),
            "character_name": character_name,
            "character_description": character_description,
            "scenes": rendered_scenes,
            "voiceover": voice_result,
            "story": story
        }

    def _add_speech_bubble(self, base_image_path: str, dialogue: str, speaker: str) -> str:
        try:
            img = Image.open(base_image_path).convert("RGBA")
            w, h = img.size

            overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)

            bubble_w = int(w * 0.85)
            bubble_h = int(h * 0.20)
            bx1 = (w - bubble_w) // 2
            by1 = int(h * 0.74)
            bx2 = bx1 + bubble_w
            by2 = by1 + bubble_h

            draw.rounded_rectangle([bx1, by1, bx2, by2], radius=16, fill=(255, 255, 255, 245), outline=(20, 20, 25, 255), width=4)
            draw.rounded_rectangle([bx1 + 15, by1 - 18, bx1 + 15 + len(speaker) * 12 + 20, by1 + 12], radius=8, fill=(255, 193, 7, 255), outline=(20, 20, 25, 255), width=2)
            
            font = ImageFont.load_default()
            draw.text((bx1 + 25, by1 - 14), speaker.upper(), fill=(0, 0, 0, 255), font=font)

            clean_diag = dialogue[:80] + "..." if len(dialogue) > 80 else dialogue
            draw.text((bx1 + 25, by1 + 22), clean_diag, fill=(20, 20, 25, 255), font=font)

            combined = Image.alpha_composite(img, overlay)
            out_path = Path(base_image_path).with_name(f"{Path(base_image_path).stem}_bubble.jpg")
            combined.convert("RGB").save(out_path, "JPEG", quality=95)
            return str(out_path)
        except Exception as e:
            logger.warning(f"Failed to add speech bubble: {e}")
            return base_image_path
