"""
AI Content Factory - Facebook Publisher
Publishes video posts and Reels to Facebook Pages via Facebook Graph API.
"""

import os
import requests
from typing import Dict, Any, Optional

from config import FACEBOOK_PAGE_ACCESS_TOKEN, FACEBOOK_PAGE_ID
from utils.helpers import logger


class FacebookPublisher:
    """Handles uploading videos and posts to Facebook Pages."""

    def __init__(
        self,
        access_token: Optional[str] = None,
        page_id: Optional[str] = None
    ):
        self.access_token = access_token or FACEBOOK_PAGE_ACCESS_TOKEN
        self.page_id = page_id or FACEBOOK_PAGE_ID
        self.graph_version = "v19.0"

    def publish_video(
        self,
        video_path: str,
        title: str,
        description: str,
        published: bool = True,
        scheduled_publish_time: Optional[int] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        logger.info(f"Initiating Facebook video publish for '{title}'...")

        if not os.path.exists(video_path):
            return {"success": False, "error": f"Video file not found: {video_path}"}

        if not self.access_token or not self.page_id or dry_run:
            sim_id = f"fb_post_{os.path.basename(video_path).replace('.mp4', '')}"
            return {
                "success": True,
                "post_id": sim_id,
                "url": f"https://facebook.com/{self.page_id or 'page'}/videos/{sim_id}",
                "mode": "simulation",
                "title": title,
                "message": "Facebook publish simulated successfully."
            }

        url = f"https://graph-video.facebook.com/{self.graph_version}/{self.page_id}/videos"
        payload = {
            "access_token": self.access_token,
            "title": title[:255],
            "description": description,
            "published": str(published).lower()
        }

        if scheduled_publish_time:
            payload["scheduled_publish_time"] = scheduled_publish_time
            payload["published"] = "false"

        try:
            with open(video_path, "rb") as video_file:
                files = {"source": video_file}
                res = requests.post(url, data=payload, files=files, timeout=120)

            if res.status_code == 200:
                data = res.json()
                video_id = data.get("id")
                return {
                    "success": True,
                    "video_id": video_id,
                    "url": f"https://facebook.com/{self.page_id}/videos/{video_id}",
                    "mode": "live"
                }
            else:
                return {"success": False, "error": res.text}
        except Exception as e:
            return {"success": False, "error": str(e)}
