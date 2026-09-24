"""
AI Content Factory - Video Creator (Standard)
Assembles scenes, stock footage, AI images, and voiceover into complete MP4 videos.
"""

import os
from pathlib import Path
from typing import List, Optional

from config import OUTPUT_DIR, RESOLUTION_MAP
from utils.helpers import logger, sanitize_filename
from utils.media_fetcher import MediaFetcher


class VideoCreator:
    """Standard Video Creation and Composition Engine."""

    def __init__(self):
        self.fetcher = MediaFetcher()

    def build_video(
        self,
        scene_media: List[str],
        voiceover_audio_path: str,
        output_filename: str = "final_video",
        orientation: str = "landscape",
        resolution: str = "1080p",
        background_music_path: Optional[str] = None,
        bg_music_volume: float = 0.12,
        fps: int = 24
    ) -> str:
        logger.info(f"Starting standard video assembly for '{output_filename}'...")

        clean_name = sanitize_filename(output_filename)
        output_path = OUTPUT_DIR / f"{clean_name}.mp4"

        dims = RESOLUTION_MAP.get(orientation, {}).get(resolution, (1920, 1080))
        target_w, target_h = dims

        try:
            from moviepy.editor import (
                AudioFileClip,
                ImageClip,
                VideoFileClip,
                CompositeAudioClip,
                concatenate_videoclips
            )

            voice_clip = AudioFileClip(voiceover_audio_path)
            total_duration = voice_clip.duration

            if not scene_media:
                bg_img = self.fetcher.create_gradient_backdrop(target_w, target_h)
                scene_media = [bg_img]

            dur_per_scene = total_duration / len(scene_media)
            clips = []

            for media_path in scene_media:
                if not os.path.exists(media_path):
                    continue

                ext = Path(media_path).suffix.lower()
                if ext in [".mp4", ".mov", ".avi", ".webm"]:
                    try:
                        vclip = VideoFileClip(media_path)
                        vclip = vclip.resize(height=target_h)
                        if vclip.w < target_w:
                            vclip = vclip.resize(width=target_w)
                        vclip = vclip.crop(x_center=vclip.w/2, y_center=vclip.h/2, width=target_w, height=target_h)
                        if vclip.duration < dur_per_scene:
                            vclip = vclip.loop(duration=dur_per_scene)
                        else:
                            vclip = vclip.subclip(0, dur_per_scene)
                        clips.append(vclip)
                    except Exception as ex:
                        logger.warning(f"Error loading video clip {media_path}: {ex}")
                else:
                    try:
                        iclip = ImageClip(media_path).set_duration(dur_per_scene)
                        iclip = iclip.resize(height=target_h)
                        if iclip.w < target_w:
                            iclip = iclip.resize(width=target_w)
                        iclip = iclip.crop(x_center=iclip.w/2, y_center=iclip.h/2, width=target_w, height=target_h)
                        clips.append(iclip)
                    except Exception as ex:
                        logger.warning(f"Error loading image clip {media_path}: {ex}")

            if not clips:
                bg_img = self.fetcher.create_gradient_backdrop(target_w, target_h)
                clips = [ImageClip(bg_img).set_duration(total_duration)]

            final_video = concatenate_videoclips(clips, method="compose")
            final_video = final_video.set_duration(total_duration)

            audio_tracks = [voice_clip]
            if background_music_path and os.path.exists(background_music_path):
                try:
                    bg_audio = AudioFileClip(background_music_path)
                    if bg_audio.duration < total_duration:
                        bg_audio = bg_audio.loop(duration=total_duration)
                    else:
                        bg_audio = bg_audio.subclip(0, total_duration)
                    bg_audio = bg_audio.volumex(bg_music_volume)
                    audio_tracks.append(bg_audio)
                except Exception as ex:
                    logger.warning(f"Error loading background music: {ex}")

            final_audio = CompositeAudioClip(audio_tracks)
            final_video = final_video.set_audio(final_audio)

            final_video.write_videofile(
                str(output_path),
                fps=fps,
                codec="libx264",
                audio_codec="aac",
                preset="fast",
                threads=4,
                logger=None
            )

            final_video.close()
            voice_clip.close()
            logger.info(f"Video created successfully: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Video assembly encountered error: {e}")
            return self._emergency_ffmpeg_assembly(scene_media, voiceover_audio_path, output_path, target_w, target_h)

    def _emergency_ffmpeg_assembly(self, media_list: list, audio_path: str, output_path: Path, width: int, height: int) -> str:
        import subprocess
        try:
            img = media_list[0] if media_list else self.fetcher.create_gradient_backdrop(width, height)
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1", "-i", str(img),
                "-i", str(audio_path),
                "-c:v", "libx264", "-tune", "stillimage",
                "-c:a", "aac", "-b:a", "192k",
                "-pix_fmt", "yuv420p",
                "-shortest",
                "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2",
                str(output_path)
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"FFmpeg emergency assembly succeeded: {output_path}")
            return str(output_path)
        except Exception as ex:
            logger.error(f"FFmpeg fallback failed: {ex}")
            return ""
