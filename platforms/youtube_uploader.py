"""
AI Content Factory - YouTube Uploader
Uploads videos, sets SEO metadata, and attaches custom thumbnails via YouTube Data API v3.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional

from config import YOUTUBE_CLIENT_SECRETS_FILE, YOUTUBE_TOKEN_FILE
from utils.helpers import logger


class YouTubeUploader:
    """Handles automated authentication and uploading to YouTube."""

    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

    def __init__(
        self,
        client_secrets_file: Optional[str] = None,
        token_file: Optional[str] = None
    ):
        self.client_secrets_file = client_secrets_file or YOUTUBE_CLIENT_SECRETS_FILE
        self.token_file = token_file or YOUTUBE_TOKEN_FILE

    def get_authenticated_service(self):
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
            from google.auth.transport.requests import Request

            creds = None
            if os.path.exists(self.token_file):
                creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                elif os.path.exists(self.client_secrets_file):
                    flow = InstalledAppFlow.from_client_secrets_file(self.client_secrets_file, self.SCOPES)
                    creds = flow.run_local_server(port=0)
                    with open(self.token_file, "w") as token:
                        token.write(creds.to_json())

            if creds:
                return build("youtube", "v3", credentials=creds)
            return None
        except Exception as e:
            logger.warning(f"YouTube OAuth authentication skipped: {e}")
            return None

    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: Optional[List[str]] = None,
        category_id: str = "28",
        privacy_status: str = "public",
        thumbnail_path: Optional[str] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        logger.info(f"Initiating YouTube upload for '{title}' (Privacy: {privacy_status})...")

        if not os.path.exists(video_path):
            return {"success": False, "error": f"Video file not found: {video_path}"}

        youtube = None if dry_run else self.get_authenticated_service()

        if not youtube or dry_run:
            simulated_id = f"sim_{os.path.basename(video_path).replace('.mp4', '')}"
            return {
                "success": True,
                "video_id": simulated_id,
                "video_url": f"https://youtu.be/{simulated_id}",
                "mode": "simulation",
                "title": title,
                "privacy": privacy_status,
                "message": "YouTube upload simulated successfully."
            }

        try:
            from googleapiclient.http import MediaFileUpload

            body = {
                "snippet": {
                    "title": title[:100],
                    "description": description,
                    "tags": tags or [],
                    "categoryId": category_id
                },
                "status": {
                    "privacyStatus": privacy_status,
                    "selfDeclaredMadeForKids": False
                }
            }

            media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
            request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
            response = request.execute()
            video_id = response.get("id")

            if thumbnail_path and os.path.exists(thumbnail_path) and video_id:
                try:
                    thumb_media = MediaFileUpload(thumbnail_path, mimetype="image/jpeg")
                    youtube.thumbnails().set(videoId=video_id, media_body=thumb_media).execute()
                except Exception as th_err:
                    logger.warning(f"Could not upload custom thumbnail: {th_err}")

            return {
                "success": True,
                "video_id": video_id,
                "video_url": f"https://youtu.be/{video_id}",
                "mode": "live",
                "title": title,
                "privacy": privacy_status
            }
        except Exception as e:
            logger.error(f"YouTube upload failed: {e}")
            return {"success": False, "error": str(e)}
