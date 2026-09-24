"""
AI Content Factory - Auto Scheduler & Full Pipeline Engine
Orchestrates the entire end-to-end autonomous video creation and publishing lifecycle.
"""

import os
import time
import schedule
from datetime import datetime
from typing import Dict, Any, Optional

from config import (
    OUTPUT_DIR,
    DEFAULT_VOICE,
    DEFAULT_RESOLUTION,
    DEFAULT_ORIENTATION,
    AUTO_SCHEDULE_INTERVAL_HOURS,
    AUTO_POST_NICHE
)
from research.trend_finder import TrendFinder
from content.script_generator import ScriptGenerator
from content.voiceover_gen import VoiceoverGenerator
from content.ai_image_gen import AIImageGenerator
from content.thumbnail_maker import ThumbnailMaker
from content.video_creator_pro import VideoCreatorPro
from seo.seo_engine import SEOEngine
from platforms.youtube_uploader import YouTubeUploader
from platforms.facebook_publisher import FacebookPublisher
from utils.media_fetcher import MediaFetcher
from utils.helpers import logger, sanitize_filename, save_json, load_json


class ContentPipeline:
    """End-to-end autonomous pipeline orchestrator."""

    def __init__(self):
        self.trend_finder = TrendFinder()
        self.script_gen = ScriptGenerator()
        self.voice_gen = VoiceoverGenerator()
        self.image_gen = AIImageGenerator()
        self.thumb_maker = ThumbnailMaker()
        self.video_creator = VideoCreatorPro()
        self.seo_engine = SEOEngine()
        self.yt_uploader = YouTubeUploader()
        self.fb_publisher = FacebookPublisher()
        self.media_fetcher = MediaFetcher()

    def run_full_pipeline(
        self,
        topic: Optional[str] = None,
        niche: str = "tech",
        content_type: str = "tech_review",
        voice: str = DEFAULT_VOICE,
        orientation: str = DEFAULT_ORIENTATION,
        resolution: str = DEFAULT_RESOLUTION,
        enable_upload: bool = False,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        start_time = time.time()
        logger.info("=" * 60)
        logger.info("🚀 STARTING AI CONTENT FACTORY FULL PIPELINE")
        logger.info("=" * 60)

        if not topic:
            logger.info(f"Discovering top trend for niche '{niche}'...")
            trends = self.trend_finder.discover_all(niche=niche)
            topic = trends[0]["title"] if trends else f"The Future of {niche.capitalize()} in 2026"

        logger.info(f"📌 Selected Topic: '{topic}'")

        script_data = self.script_gen.generate_script(
            topic=topic,
            content_type=content_type,
            target_duration="60s"
        )
        video_title = script_data.get("title", topic)

        voice_res = self.voice_gen.generate(
            text=script_data.get("full_voiceover_text", topic),
            output_name=f"voice_{sanitize_filename(video_title[:25])}",
            voice=voice
        )
        audio_path = voice_res.get("audio_path")
        srt_path = voice_res.get("srt_path")

        scenes = script_data.get("scenes", [])
        scene_media = []

        for sc in scenes:
            query = sc.get("pexels_query", topic)
            pexels_vids = self.media_fetcher.fetch_pexels_videos(query=query, orientation=orientation, per_page=1)
            if pexels_vids:
                scene_media.append(pexels_vids[0])
            else:
                ai_prompt = sc.get("visual_prompt") or sc.get("narration") or topic
                img = self.image_gen.generate_image(
                    prompt=ai_prompt,
                    style="cinematic",
                    width=1920 if orientation == "landscape" else 1080,
                    height=1080 if orientation == "landscape" else 1920
                )
                scene_media.append(img)

        music_path = self.media_fetcher.generate_ambient_track()

        final_video_path = self.video_creator.build_pro_video(
            scene_media=scene_media,
            voiceover_audio_path=audio_path,
            output_filename=f"video_{sanitize_filename(video_title[:30])}",
            orientation=orientation,
            resolution=resolution,
            background_music_path=music_path,
            enable_ken_burns=True
        )

        thumb_bg = scene_media[0] if (scene_media and scene_media[0].endswith((".jpg", ".png"))) else None
        thumb_path = self.thumb_maker.create_thumbnail(
            title=video_title[:30],
            background_image=thumb_bg,
            ai_prompt=topic if not thumb_bg else None,
            badge_text="2026 UPDATE",
            output_filename=f"thumb_{sanitize_filename(video_title[:30])}"
        )

        seo_data = self.seo_engine.optimize_video_seo(
            topic=video_title,
            script_data=script_data,
            target_niche=niche
        )

        yt_result = None
        fb_result = None
        if enable_upload:
            yt_result = self.yt_uploader.upload_video(
                video_path=final_video_path,
                title=seo_data.get("best_title", video_title),
                description=seo_data.get("description", ""),
                tags=seo_data.get("tags", []),
                thumbnail_path=thumb_path,
                dry_run=dry_run
            )

            fb_result = self.fb_publisher.publish_video(
                video_path=final_video_path,
                title=seo_data.get("best_title", video_title),
                description=seo_data.get("description", ""),
                dry_run=dry_run
            )

        elapsed = round(time.time() - start_time, 2)
        logger.info(f"✨ FULL PIPELINE COMPLETED IN {elapsed} SECONDS!")

        record = {
            "timestamp": datetime.now().isoformat(),
            "topic": topic,
            "title": video_title,
            "content_type": content_type,
            "niche": niche,
            "video_path": final_video_path,
            "thumbnail_path": thumb_path,
            "audio_path": audio_path,
            "srt_path": srt_path,
            "seo": seo_data,
            "youtube": yt_result,
            "facebook": fb_result,
            "elapsed_seconds": elapsed
        }

        self._save_history(record)
        return record

    def _save_history(self, record: Dict[str, Any]):
        history_file = OUTPUT_DIR / "pipeline_history.json"
        history = load_json(history_file, default=[])
        history.append(record)
        save_json(history, history_file)


def start_scheduler(
    interval_hours: int = AUTO_SCHEDULE_INTERVAL_HOURS,
    niche: str = AUTO_POST_NICHE
):
    pipeline = ContentPipeline()
    logger.info(f"⏰ Starting AI Content Factory Scheduler (Interval: every {interval_hours} hours, Niche: '{niche}')...")

    def job():
        try:
            pipeline.run_full_pipeline(
                niche=niche,
                enable_upload=True,
                dry_run=False
            )
        except Exception as e:
            logger.error(f"Scheduled pipeline run failed: {e}")

    job()
    schedule.every(interval_hours).hours.do(job)

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    start_scheduler()

