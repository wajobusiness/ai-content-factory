"""
AI Content Factory Pro - REST API Server
Provides programmatic endpoints for triggering automated video generation,
retrieving trends, publishing to connected accounts, and receiving webhooks.

Usage:
    python3 api.py               # Starts standalone REST API server on port 8000
"""

import os
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any

from auto_scheduler import ContentPipeline
from research.trend_finder import TrendFinder
from platforms.account_manager import AccountManager
from platforms.youtube_uploader import YouTubeUploader
from platforms.facebook_publisher import FacebookPublisher
from utils.helpers import logger


class ContentAPIHandler(BaseHTTPRequestHandler):
    """HTTP Request handler implementing AI Content Factory REST API."""

    def _send_json(self, data: Dict[str, Any], status_code: int = 200):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))

    def do_OPTIONS(self):
        self._send_json({"status": "ok"}, 200)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/api/v1/health" or path == "/health":
            self._send_json({
                "status": "healthy",
                "version": "2.5.0",
                "engine": "AI Content Factory Pro",
                "timestamp": int(time.time())
            })
            return

        elif path == "/api/v1/trends":
            niche = query.get("niche", ["tech"])[0]
            finder = TrendFinder()
            trends = finder.discover_all(niche=niche)
            self._send_json({"niche": niche, "count": len(trends), "trends": trends})
            return

        elif path == "/api/v1/accounts":
            acct = AccountManager()
            all_accts = acct.get_all_accounts()
            # Mask secrets for safety
            safe_accts = json.loads(json.dumps(all_accts))
            if "facebook" in safe_accts and safe_accts["facebook"].get("access_token"):
                safe_accts["facebook"]["access_token"] = "***" + safe_accts["facebook"]["access_token"][-4:]
            self._send_json({"accounts": safe_accts})
            return

        else:
            self._send_json({"error": "Endpoint not found", "path": path}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        content_length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(content_length) if content_length > 0 else b"{}"
        
        try:
            body = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
        except Exception:
            body = {}

        if path == "/api/v1/generate":
            topic = body.get("topic")
            niche = body.get("niche", "tech")
            content_type = body.get("content_type", "shorts")
            voice = body.get("voice", "en-US-GuyNeural")
            orientation = body.get("orientation", "vertical")
            resolution = body.get("resolution", "1080p")
            auto_publish = body.get("auto_publish", False)

            pipeline = ContentPipeline()
            logger.info(f"API Request: Generating content for '{topic or niche}'...")
            
            try:
                res = pipeline.run_full_pipeline(
                    topic=topic,
                    niche=niche,
                    content_type=content_type,
                    voice=voice,
                    orientation=orientation,
                    resolution=resolution,
                    enable_upload=auto_publish,
                    dry_run=not auto_publish
                )
                self._send_json({
                    "success": True,
                    "message": "Content generated successfully",
                    "result": res
                }, 200)
            except Exception as e:
                self._send_json({"success": False, "error": str(e)}, 500)
            return

        elif path == "/api/v1/publish":
            video_path = body.get("video_path")
            title = body.get("title", "AI Video")
            description = body.get("description", "")
            platform = body.get("platform", "youtube").lower()
            dry_run = body.get("dry_run", False)

            if not video_path or not os.path.exists(video_path):
                self._send_json({"success": False, "error": f"Video file not found: {video_path}"}, 400)
                return

            if platform == "youtube":
                yt = YouTubeUploader()
                res = yt.upload_video(video_path=video_path, title=title, description=description, dry_run=dry_run)
                self._send_json({"success": res.get("success", False), "result": res})
            elif platform == "facebook":
                fb = FacebookPublisher()
                res = fb.publish_video(video_path=video_path, title=title, description=description, dry_run=dry_run)
                self._send_json({"success": res.get("success", False), "result": res})
            else:
                self._send_json({"success": False, "error": f"Unsupported platform '{platform}'"}, 400)
            return

        else:
            self._send_json({"error": "Endpoint not found", "path": path}, 404)


def run_api_server(port: int = 8000):
    server_address = ("", port)
    httpd = HTTPServer(server_address, ContentAPIHandler)
    logger.info(f"⚡ AI Content Factory REST API server running on http://0.0.0.0:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    run_api_server(port=port)
