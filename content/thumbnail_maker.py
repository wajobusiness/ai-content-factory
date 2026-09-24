"""
AI Content Factory - Thumbnail Maker
Creates high-CTR, eye-catching thumbnails with bold typography, badges, gradients, and strokes.
"""

import os
from pathlib import Path
from typing import Optional, List
from PIL import Image, ImageDraw, ImageFont

from config import OUTPUT_DIR, FONTS_DIR
from utils.helpers import logger, sanitize_filename
from content.ai_image_gen import AIImageGenerator


class ThumbnailMaker:
    """Automated high-conversion thumbnail creator using Pillow."""

    COLORS = {
        "yellow": (255, 230, 0),
        "white": (255, 255, 255),
        "red": (255, 45, 85),
        "cyan": (0, 240, 255),
        "neon_green": (57, 255, 20),
        "orange": (255, 140, 0),
        "black": (15, 15, 20),
    }

    def __init__(self):
        self.image_gen = AIImageGenerator()

    def create_thumbnail(
        self,
        title: str,
        background_image: Optional[str] = None,
        ai_prompt: Optional[str] = None,
        badge_text: Optional[str] = None,
        main_color: str = "yellow",
        output_filename: str = "thumbnail",
        width: int = 1280,
        height: int = 720
    ) -> str:
        logger.info(f"Designing thumbnail for '{title}'...")

        if background_image and os.path.exists(background_image):
            bg = Image.open(background_image).convert("RGBA")
            bg = bg.resize((width, height), Image.Resampling.LANCZOS)
        elif ai_prompt:
            ai_img_path = self.image_gen.generate_image(
                prompt=ai_prompt,
                style="cinematic",
                width=width,
                height=height
            )
            bg = Image.open(ai_img_path).convert("RGBA")
            bg = bg.resize((width, height), Image.Resampling.LANCZOS)
        else:
            bg = Image.new("RGBA", (width, height), (15, 23, 42, 255))
            draw_bg = ImageDraw.Draw(bg)
            for y in range(height):
                ratio = y / height
                r = int(15 * (1 - ratio) + 30 * ratio)
                g = int(23 * (1 - ratio) + 40 * ratio)
                b = int(42 * (1 - ratio) + 80 * ratio)
                draw_bg.line([(0, y), (width, y)], fill=(r, g, b, 255))

        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 90))
        bg = Image.alpha_composite(bg, overlay)

        vignette = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        v_draw = ImageDraw.Draw(vignette)
        v_draw.rectangle([0, 0, width, height], outline=(255, 45, 85, 200), width=8)
        bg = Image.alpha_composite(bg, vignette)

        draw = ImageDraw.Draw(bg)

        font_size = int(height * 0.12)
        font = self._get_font(font_size)
        badge_font = self._get_font(int(height * 0.055))

        title_upper = title.upper()
        lines = self._wrap_text(title_upper, max_chars_per_line=18)

        text_color = self.COLORS.get(main_color.lower(), self.COLORS["yellow"])
        start_y = int(height * 0.25)

        if badge_text:
            badge_str = badge_text.upper()
            badge_bbox = badge_font.getbbox(badge_str) if hasattr(badge_font, 'getbbox') else (0, 0, len(badge_str)*15, 30)
            bw = badge_bbox[2] - badge_bbox[0] + 40
            bh = badge_bbox[3] - badge_bbox[1] + 20
            bx = 60
            by = 60
            self._draw_rounded_rectangle(draw, [bx, by, bx + bw, by + bh], radius=12, fill=(255, 45, 85, 240))
            draw.text((bx + 20, by + 8), badge_str, font=badge_font, fill=(255, 255, 255))
            start_y = by + bh + 40

        current_y = start_y
        for i, line in enumerate(lines):
            for dx, dy in [(-3, -3), (-3, 3), (3, -3), (3, 3), (0, 4), (4, 0), (-4, 0), (0, -4), (5, 5)]:
                draw.text((60 + dx, current_y + dy), line, font=font, fill=(0, 0, 0, 255))

            line_color = text_color if i % 2 == 0 else self.COLORS["white"]
            draw.text((60, current_y), line, font=font, fill=line_color)
            current_y += int(font_size * 1.25)

        clean_name = sanitize_filename(output_filename)
        final_path = OUTPUT_DIR / f"{clean_name}.jpg"
        final_rgb = bg.convert("RGB")
        final_rgb.save(final_path, "JPEG", quality=95)
        logger.info(f"Thumbnail saved: {final_path}")
        return str(final_path)

    def create_thumbnail_variants(
        self,
        title: str,
        background_image: Optional[str] = None,
        ai_prompt: Optional[str] = None,
        output_base: str = "thumb_variant"
    ) -> List[Dict[str, str]]:
        """Generates 3 distinct A/B test thumbnail variants with different colorways and badges."""
        configs = [
            {"style": "Neon Gold & Alert", "color": "yellow", "badge": "🔥 VIRAL 2026", "suffix": "A"},
            {"style": "High-Contrast Crimson", "color": "red", "badge": "⚠️ MUST WATCH", "suffix": "B"},
            {"style": "Cyber Cyan Electric", "color": "cyan", "badge": "⚡ BREAKTHROUGH", "suffix": "C"}
        ]
        results = []
        for cfg in configs:
            path = self.create_thumbnail(
                title=title,
                background_image=background_image,
                ai_prompt=ai_prompt,
                badge_text=cfg["badge"],
                main_color=cfg["color"],
                output_filename=f"{output_base}_{cfg['suffix']}"
            )
            results.append({
                "style": cfg["style"],
                "path": path,
                "variant": cfg["suffix"],
                "color": cfg["color"],
                "badge": cfg["badge"]
            })
        return results

    def _get_font(self, size: int) -> ImageFont.ImageFont:
        candidate_paths = [
            "/System/Library/Fonts/Supplemental/Impact.ttf",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/Library/Fonts/Arial Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            str(FONTS_DIR / "bold.ttf")
        ]
        for p in candidate_paths:
            if os.path.exists(p):
                try:
                    return ImageFont.truetype(p, size)
                except Exception:
                    pass
        return ImageFont.load_default()

    def _wrap_text(self, text: str, max_chars_per_line: int = 18) -> List[str]:
        words = text.split()
        lines = []
        current_line = []
        current_len = 0

        for w in words:
            if current_len + len(w) + 1 <= max_chars_per_line:
                current_line.append(w)
                current_len += len(w) + 1
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [w]
                current_len = len(w)

        if current_line:
            lines.append(" ".join(current_line))

        return lines[:3]

    def _draw_rounded_rectangle(self, draw: ImageDraw.ImageDraw, bounds: list, radius: int = 10, fill: tuple = (255, 0, 0)):
        x1, y1, x2, y2 = bounds
        draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
        draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
        draw.pieslice([x1, y1, x1 + 2 * radius, y1 + 2 * radius], 180, 270, fill=fill)
        draw.pieslice([x2 - 2 * radius, y1, x2, y1 + 2 * radius], 270, 360, fill=fill)
        draw.pieslice([x1, y2 - 2 * radius, x1 + 2 * radius, y2], 90, 180, fill=fill)
        draw.pieslice([x2 - 2 * radius, y2 - 2 * radius, x2, y2], 0, 90, fill=fill)
