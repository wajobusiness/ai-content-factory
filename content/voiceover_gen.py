"""
AI Content Factory - Voiceover Generator
Generates studio-quality AI voiceover and synchronized SRT subtitles using Edge-TTS (100% Free).
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

from config import DEFAULT_VOICE, DEFAULT_VOICE_RATE, DEFAULT_VOICE_PITCH, TEMP_DIR, OUTPUT_DIR
from utils.helpers import logger, sanitize_filename


class VoiceoverGenerator:
    """High-quality neural TTS voiceover and subtitle generator."""

    def __init__(
        self,
        voice: str = DEFAULT_VOICE,
        rate: str = DEFAULT_VOICE_RATE,
        pitch: str = DEFAULT_VOICE_PITCH
    ):
        self.voice = voice
        self.rate = rate
        self.pitch = pitch

    async def _async_generate_edge_tts(
        self,
        text: str,
        audio_path: Path,
        srt_path: Optional[Path] = None,
        voice: Optional[str] = None,
        rate: Optional[str] = None,
        pitch: Optional[str] = None
    ) -> bool:
        import edge_tts

        selected_voice = voice or self.voice
        selected_rate = rate or self.rate
        selected_pitch = pitch or self.pitch

        communicate = edge_tts.Communicate(
            text=text,
            voice=selected_voice,
            rate=selected_rate,
            pitch=selected_pitch
        )

        submaker = edge_tts.SubMaker()
        with open(audio_path, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    submaker.feed(chunk)

        if srt_path:
            srt_content = submaker.get_srt()
            with open(srt_path, "w", encoding="utf-8") as f:
                f.write(srt_content)

        return True

    def generate(
        self,
        text: str,
        output_name: str = "voiceover",
        voice: Optional[str] = None,
        rate: Optional[str] = None,
        pitch: Optional[str] = None,
        generate_subtitles: bool = True
    ) -> Dict[str, Any]:
        clean_name = sanitize_filename(output_name)
        audio_path = OUTPUT_DIR / f"{clean_name}.mp3"
        srt_path = OUTPUT_DIR / f"{clean_name}.srt" if generate_subtitles else None

        logger.info(f"Generating voiceover using voice '{voice or self.voice}'...")

        success = False
        try:
            try:
                import nest_asyncio
                nest_asyncio.apply()
            except Exception:
                pass

            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            loop.run_until_complete(
                self._async_generate_edge_tts(text, audio_path, srt_path, voice, rate, pitch)
            )

            if audio_path.exists() and audio_path.stat().st_size > 100:
                success = True
        except Exception as e:
            logger.warning(f"Edge-TTS generation encountered issue: {e}")

        if not success:
            from utils.media_fetcher import MediaFetcher
            fetcher = MediaFetcher()
            fallback_wav = OUTPUT_DIR / f"{clean_name}.wav"
            fetcher.generate_ambient_track(fallback_wav, duration_seconds=15)
            audio_path = fallback_wav

        duration = self.get_audio_duration(audio_path)

        if generate_subtitles and srt_path and (not srt_path.exists() or srt_path.stat().st_size == 0):
            self._generate_basic_srt(text, duration, srt_path)

        return {
            "audio_path": str(audio_path),
            "srt_path": str(srt_path) if srt_path and srt_path.exists() else None,
            "duration": duration,
            "voice": voice or self.voice,
            "text": text
        }

    def get_audio_duration(self, audio_path: Path) -> float:
        try:
            from moviepy.editor import AudioFileClip
            clip = AudioFileClip(str(audio_path))
            dur = clip.duration
            clip.close()
            return float(dur)
        except Exception:
            return 10.0

    def _generate_basic_srt(self, text: str, total_duration: float, srt_path: Path):
        sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
        if not sentences:
            sentences = [text]

        time_per_sentence = total_duration / max(1, len(sentences))
        lines = []

        for i, sentence in enumerate(sentences):
            start_sec = i * time_per_sentence
            end_sec = (i + 1) * time_per_sentence
            
            start_str = self._format_srt_time(start_sec)
            end_str = self._format_srt_time(end_sec)

            lines.append(f"{i + 1}")
            lines.append(f"{start_str} --> {end_str}")
            lines.append(sentence)
            lines.append("")

        with open(srt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def _format_srt_time(self, seconds: float) -> str:
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        msecs = int((seconds - int(seconds)) * 1000)
        return f"{hrs:02d}:{mins:02d}:{secs:02d},{msecs:03d}"
