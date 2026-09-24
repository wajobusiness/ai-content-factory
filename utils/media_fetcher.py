"""
AI Content Factory - Media Fetcher
Fetches free stock footage (Pexels), royalty-free audio, and synthetic visuals.
"""

import time
import random
import requests
from pathlib import Path
from typing import List, Optional, Dict
from PIL import Image, ImageDraw, ImageFont

from config import PEXELS_API_KEY, TEMP_DIR, MUSIC_DIR
from utils.helpers import logger, sanitize_filename


class MediaFetcher:
    """Handles fetching and downloading stock videos, images, and music."""

    def __init__(self, pexels_api_key: Optional[str] = None):
        self.pexels_api_key = pexels_api_key or PEXELS_API_KEY
        self.headers = {"Authorization": self.pexels_api_key} if self.pexels_api_key else {}

    def fetch_pexels_videos(
        self,
        query: str,
        orientation: str = "landscape",
        per_page: int = 3,
        min_duration: int = 3,
        max_duration: int = 30
    ) -> List[str]:
        if not self.pexels_api_key:
            logger.warning("No Pexels API key provided. Skipping Pexels video fetch.")
            return []

        url = "https://api.pexels.com/videos/search"
        params = {
            "query": query,
            "orientation": orientation,
            "per_page": per_page,
            "size": "medium"
        }

        try:
            res = requests.get(url, headers=self.headers, params=params, timeout=15)
            if res.status_code != 200:
                logger.warning(f"Pexels API video search failed ({res.status_code}): {res.text[:100]}")
                return []

            data = res.json()
            videos = data.get("videos", [])
            downloaded_paths = []

            for i, vid in enumerate(videos):
                dur = vid.get("duration", 0)
                if dur < min_duration or dur > max_duration:
                    continue

                video_files = vid.get("video_files", [])
                video_files.sort(key=lambda x: x.get("width", 0), reverse=True)

                download_url = None
                for vf in video_files:
                    if vf.get("file_type") == "video/mp4":
                        download_url = vf.get("link")
                        break

                if not download_url and video_files:
                    download_url = video_files[0].get("link")

                if download_url:
                    target_file = TEMP_DIR / f"pexels_{sanitize_filename(query)}_{i}_{vid.get('id')}.mp4"
                    if self.download_file(download_url, target_file):
                        downloaded_paths.append(str(target_file))

            return downloaded_paths

        except Exception as e:
            logger.error(f"Error fetching videos from Pexels: {e}")
            return []

    def fetch_pexels_photos(
        self,
        query: str,
        orientation: str = "landscape",
        per_page: int = 5
    ) -> List[str]:
        if not self.pexels_api_key:
            logger.warning("No Pexels API key provided. Skipping Pexels photo fetch.")
            return []

        url = "https://api.pexels.com/v1/search"
        params = {
            "query": query,
            "orientation": orientation,
            "per_page": per_page
        }

        try:
            res = requests.get(url, headers=self.headers, params=params, timeout=15)
            if res.status_code != 200:
                return []

            data = res.json()
            photos = data.get("photos", [])
            downloaded_paths = []

            for i, photo in enumerate(photos):
                src = photo.get("src", {})
                img_url = src.get("large2x") or src.get("large") or src.get("original")
                if img_url:
                    target_file = TEMP_DIR / f"pexels_img_{sanitize_filename(query)}_{i}_{photo.get('id')}.jpg"
                    if self.download_file(img_url, target_file):
                        downloaded_paths.append(str(target_file))

            return downloaded_paths

        except Exception as e:
            logger.error(f"Error fetching photos from Pexels: {e}")
            return []

    def download_file(self, url: str, target_path: Path) -> bool:
        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with requests.get(url, stream=True, timeout=30) as r:
                r.raise_for_status()
                with open(target_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            return True
        except Exception as e:
            logger.error(f"Failed to download {url}: {e}")
            return False

    def generate_ambient_track(self, output_path: Optional[Path] = None, duration_seconds: int = 60) -> str:
        import wave
        import struct
        import math

        if output_path is None:
            output_path = MUSIC_DIR / "ambient_chill.wav"
        else:
            output_path = Path(output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        if output_path.exists() and output_path.stat().st_size > 1000:
            return str(output_path)

        sample_rate = 44100
        num_samples = sample_rate * duration_seconds

        chord_progression = [
            [146.83, 220.00, 329.63], # Dm9
            [174.61, 261.63, 329.63], # Fmaj7
            [130.81, 196.00, 261.63], # Cmaj
            [110.00, 164.81, 220.00], # Am
        ]

        chord_dur = 4.0

        with wave.open(str(output_path), "w") as wav_file:
            wav_file.setnchannels(2)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)

            for i in range(num_samples):
                t = i / sample_rate
                chord_idx = int((t / chord_dur) % len(chord_progression))
                chord = chord_progression[chord_idx]

                l_val = 0.0
                r_val = 0.0

                lfo = (1.0 + 0.2 * math.sin(2 * math.pi * 0.2 * t))

                for idx, freq in enumerate(chord):
                    f_left = freq * (1.0 - 0.001 * idx)
                    f_right = freq * (1.0 + 0.001 * idx)

                    amp = (0.25 / len(chord)) * lfo
                    l_val += amp * math.sin(2 * math.pi * f_left * t)
                    r_val += amp * math.sin(2 * math.pi * f_right * t)

                fade_time = 2.0
                if t < fade_time:
                    gain = t / fade_time
                elif t > (duration_seconds - fade_time):
                    gain = (duration_seconds - t) / fade_time
                else:
                    gain = 1.0

                l_sample = int(max(-32767, min(32767, l_val * gain * 32767 * 0.35)))
                r_sample = int(max(-32767, min(32767, r_val * gain * 32767 * 0.35)))

                wav_file.writeframes(struct.pack("<hh", l_sample, r_sample))

        logger.info(f"Generated procedural ambient background audio: {output_path}")
        return str(output_path)

    def create_gradient_backdrop(
        self,
        width: int = 1920,
        height: int = 1080,
        color_start: tuple = (20, 30, 48),
        color_end: tuple = (36, 59, 85),
        title_text: Optional[str] = None,
        output_path: Optional[Path] = None
    ) -> str:
        if output_path is None:
            output_path = TEMP_DIR / f"gradient_{random.randint(1000, 9999)}.jpg"
        else:
            output_path = Path(output_path)

        base = Image.new("RGB", (width, height), color_start)
        draw = ImageDraw.Draw(base)

        for y in range(height):
            ratio = y / height
            r = int(color_start[0] * (1 - ratio) + color_end[0] * ratio)
            g = int(color_start[1] * (1 - ratio) + color_end[1] * ratio)
            b = int(color_start[2] * (1 - ratio) + color_end[2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        if title_text:
            try:
                font = ImageFont.load_default()
                draw.text((width // 2, height // 2), title_text, fill=(255, 255, 255), anchor="mm")
            except Exception:
                pass

        base.save(output_path, "JPEG", quality=95)
        return str(output_path)
