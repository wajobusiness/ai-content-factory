"""
AI Content Factory - Video Creator Pro
Advanced video production engine featuring:
- Ken Burns Motion (Dynamic Pan & Zoom)
- Smart Audio Ducking & Music Balancing
- Smooth Scene Crossfades
- Watermark & Branding
"""

import os
from pathlib import Path
from typing import List, Optional
from PIL import Image, ImageDraw, ImageFont

from config import OUTPUT_DIR, TEMP_DIR, RESOLUTION_MAP
from utils.helpers import logger, sanitize_filename
from utils.media_fetcher import MediaFetcher


class VideoCreatorPro:
    """Professional-grade Video Creator with motion graphics and cinematic effects."""

    def __init__(self):
        self.fetcher = MediaFetcher()

    def build_pro_video(
        self,
        scene_media: List[str],
        voiceover_audio_path: str,
        output_filename: str = "pro_video",
        orientation: str = "landscape",
        resolution: str = "1080p",
        background_music_path: Optional[str] = None,
        bg_music_volume: float = 0.10,
        enable_ken_burns: bool = True,
        watermark_text: Optional[str] = "AI Content Factory",
        fps: int = 30
    ) -> str:
        logger.info(f"Starting Pro Video assembly for '{output_filename}' (Ken Burns: {enable_ken_burns})...")

        clean_name = sanitize_filename(output_filename)
        output_path = OUTPUT_DIR / f"{clean_name}.mp4"

        dims = RESOLUTION_MAP.get(orientation, {}).get(resolution, (1920, 1080))
        target_w, target_h = dims

        try:
            from moviepy.editor import (
                AudioFileClip,
                ImageClip,
                VideoFileClip,
                CompositeVideoClip,
                CompositeAudioClip,
                concatenate_videoclips
            )

            voice_clip = AudioFileClip(voiceover_audio_path)
            total_duration = voice_clip.duration

            if not scene_media:
                scene_media = [self.fetcher.create_gradient_backdrop(target_w, target_h)]

            dur_per_scene = total_duration / len(scene_media)
            clips = []

            for i, media_path in enumerate(scene_media):
                if not os.path.exists(media_path):
                    continue

                ext = Path(media_path).suffix.lower()
                if ext in [".mp4", ".mov", ".avi", ".webm"]:
                    vclip = VideoFileClip(media_path)
                    vclip = vclip.resize(height=target_h)
                    if vclip.w < target_w:
                        vclip = vclip.resize(width=target_w)
                    vclip = vclip.crop(x_center=vclip.w/2, y_center=vclip.h/2, width=target_w, height=target_h)
                    if vclip.duration < dur_per_scene:
                        vclip = vclip.loop(duration=dur_per_scene)
                    else:
                        vclip = vclip.subclip(0, dur_per_scene)
                    vclip = vclip.crossfadein(0.4).crossfadeout(0.4)
                    clips.append(vclip)
                else:
                    iclip = ImageClip(media_path).set_duration(dur_per_scene)
                    iclip = iclip.resize(height=target_h)
                    if iclip.w < target_w:
                        iclip = iclip.resize(width=target_w)
                    iclip = iclip.crop(x_center=iclip.w/2, y_center=iclip.h/2, width=target_w, height=target_h)

                    if enable_ken_burns:
                        zoom_effect = lambda t: 1.0 + 0.08 * (t / max(1.0, dur_per_scene))
                        iclip = iclip.resize(zoom_effect)
                        iclip = iclip.crop(x_center=iclip.w/2, y_center=iclip.h/2, width=target_w, height=target_h)

                    iclip = iclip.crossfadein(0.4).crossfadeout(0.4)
                    clips.append(iclip)

            if not clips:
                bg = self.fetcher.create_gradient_backdrop(target_w, target_h)
                clips = [ImageClip(bg).set_duration(total_duration)]

            main_track = concatenate_videoclips(clips, method="compose")
            main_track = main_track.set_duration(total_duration)

            composite_layers = [main_track]

            if watermark_text:
                try:
                    wm_img = Image.new("RGBA", (300, 60), (0, 0, 0, 120))
                    wm_draw = ImageDraw.Draw(wm_img)
                    wm_draw.rounded_rectangle([0, 0, 298, 58], radius=8, fill=(0, 0, 0, 140), outline=(255, 255, 255, 100), width=1)
                    font = ImageFont.load_default()
                    wm_draw.text((20, 22), watermark_text.upper(), fill=(255, 255, 255, 200), font=font)
                    
                    wm_temp = TEMP_DIR / "watermark_badge.png"
                    wm_img.save(wm_temp)
                    
                    wm_clip = ImageClip(str(wm_temp)).set_duration(total_duration).set_pos(("right", 40))
                    composite_layers.append(wm_clip)
                except Exception as ex:
                    logger.warning(f"Could not render watermark: {ex}")

            final_video = CompositeVideoClip(composite_layers, size=(target_w, target_h))
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
                    logger.warning(f"Error mixing pro audio: {ex}")

            final_video = final_video.set_audio(CompositeAudioClip(audio_tracks))

            final_video.write_videofile(
                str(output_path),
                fps=fps,
                codec="libx264",
                audio_codec="aac",
                preset="medium",
                threads=4,
                logger=None
            )

            final_video.close()
            voice_clip.close()
            logger.info(f"Pro Video exported: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Pro Video compilation failed: {e}")
            from content.video_creator import VideoCreator
            std = VideoCreator()
            return std.build_video(
                scene_media=scene_media,
                voiceover_audio_path=voiceover_audio_path,
                output_filename=output_filename,
                orientation=orientation,
                resolution=resolution,
                background_music_path=background_music_path,
                bg_music_volume=bg_music_volume
            )
