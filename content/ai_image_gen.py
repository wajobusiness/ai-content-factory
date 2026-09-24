"""
AI Content Factory - AI Image Generator
Generates high-resolution images via Pollinations.ai (100% Free & Unlimited).
Supports styles: Cinematic, 3D Cartoon, Anime, Cyberpunk, Photorealistic.
"""

import time
import urllib.parse
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import requests
except ImportError:
    requests = None

from config import TEMP_DIR, OUTPUT_DIR
from utils.helpers import logger, sanitize_filename
from utils.media_fetcher import MediaFetcher


class AIImageGenerator:
    """Free AI Image Generator powered by Pollinations.ai."""

    STYLE_MODIFIERS = {
        "cinematic": "cinematic 8k octane render, dramatic lighting, photorealistic, intricate details, hyper-detailed, masterpiece",
        "3d_cartoon": "3D Pixar Disney animation style, smooth vibrant lighting, friendly expressive character, cute 3d render",
        "anime": "vibrant Japanese anime style, Studio Ghibli inspired, breathtaking skies, rich colors, detailed illustration",
        "cyberpunk": "cyberpunk neon atmosphere, futuristic dark city, glowing holograms, reflections on wet pavement, high tech",
        "photorealistic": "award winning National Geographic photograph, 85mm f1.4 lens, natural lighting, hyperrealistic, sharp focus",
        "digital_art": "epic concept art, dynamic composition, trending on ArtStation, vivid digital painting"
    }

    def __init__(self):
        self.fetcher = MediaFetcher()

    def generate_image(
        self,
        prompt: str,
        style: str = "cinematic",
        width: int = 1280,
        height: int = 720,
        seed: Optional[int] = None,
        model: str = "flux",
        output_filename: Optional[str] = None
    ) -> str:
        modifier = self.STYLE_MODIFIERS.get(style.lower(), self.STYLE_MODIFIERS["cinematic"])
        enhanced_prompt = f"{prompt}, {modifier}"
        
        logger.info(f"Generating AI image: '{prompt[:40]}...' (Style: {style}, {width}x{height})")

        encoded_prompt = urllib.parse.quote_plus(enhanced_prompt)
        current_seed = seed or int(time.time() * 1000) % 1000000

        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&seed={current_seed}&nologo=true&model={model}"

        clean_name = sanitize_filename(output_filename or f"img_{prompt[:30]}_{current_seed}")
        target_path = TEMP_DIR / f"{clean_name}.jpg"

        success = False
        if requests:
            for attempt in range(2):
                try:
                    res = requests.get(url, timeout=12)
                    if res.status_code == 200 and len(res.content) > 5000:
                        with open(target_path, "wb") as f:
                            f.write(res.content)
                        success = True
                        logger.info(f"AI Image downloaded successfully: {target_path}")
                        break
                    time.sleep(1)
                except Exception as e:
                    logger.warning(f"Pollinations fetch attempt {attempt+1} failed: {e}")
                    time.sleep(1)

        if not success:
            logger.info("Using procedural visual canvas fallback.")
            target_path = Path(self.fetcher.create_gradient_backdrop(
                width=width,
                height=height,
                title_text=prompt[:50],
                output_path=target_path
            ))

        return str(target_path)

