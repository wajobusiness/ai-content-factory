"""
Account & API Credentials Manager for AI Content Factory SaaS.
Allows users to connect, test, and persist their YouTube, Facebook, TikTok/Webhook, and AI API accounts.
"""

import os
import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional
from config import (
    OUTPUT_DIR,
    GROQ_API_KEY,
    GEMINI_API_KEY,
    PEXELS_API_KEY,
    FACEBOOK_PAGE_ACCESS_TOKEN,
    FACEBOOK_PAGE_ID,
    YOUTUBE_CLIENT_SECRETS_FILE,
    YOUTUBE_TOKEN_FILE
)
from utils.helpers import logger, save_json, load_json

ACCOUNTS_FILE = OUTPUT_DIR / "connected_accounts.json"


class AccountManager:
    """Handles multi-platform social accounts and API key persistence."""

    def __init__(self):
        self.accounts_file = ACCOUNTS_FILE
        self._ensure_file()

    def _ensure_file(self):
        if not self.accounts_file.exists():
            default_config = {
                "youtube": {
                    "channel_name": "My YouTube Channel",
                    "client_secrets_path": str(YOUTUBE_CLIENT_SECRETS_FILE),
                    "token_path": str(YOUTUBE_TOKEN_FILE),
                    "connected": False,
                    "auto_publish": False
                },
                "facebook": {
                    "page_name": "My Facebook Page",
                    "page_id": FACEBOOK_PAGE_ID,
                    "access_token": FACEBOOK_PAGE_ACCESS_TOKEN,
                    "connected": bool(FACEBOOK_PAGE_ACCESS_TOKEN and FACEBOOK_PAGE_ID),
                    "auto_publish": False
                },
                "webhook": {
                    "name": "Custom Automation Webhook (Make/Zapier/n8n/TikTok)",
                    "url": "",
                    "secret_token": "",
                    "connected": False,
                    "auto_publish": False
                },
                "ai_engines": {
                    "groq_api_key": GROQ_API_KEY,
                    "gemini_api_key": GEMINI_API_KEY,
                    "pexels_api_key": PEXELS_API_KEY
                }
            }
            save_json(default_config, self.accounts_file)

    def get_all_accounts(self) -> Dict[str, Any]:
        """Loads all connected accounts and keys."""
        return load_json(self.accounts_file, default={})

    def save_youtube_account(self, channel_name: str, client_secrets_path: str = "", token_path: str = "") -> Dict[str, Any]:
        data = self.get_all_accounts()
        data.setdefault("youtube", {})
        data["youtube"]["channel_name"] = channel_name
        if client_secrets_path:
            data["youtube"]["client_secrets_path"] = client_secrets_path
        if token_path:
            data["youtube"]["token_path"] = token_path
        data["youtube"]["connected"] = os.path.exists(data["youtube"].get("token_path", "")) or os.path.exists(data["youtube"].get("client_secrets_path", ""))
        save_json(data, self.accounts_file)
        return data["youtube"]

    def save_facebook_account(self, page_name: str, page_id: str, access_token: str) -> Dict[str, Any]:
        data = self.get_all_accounts()
        data.setdefault("facebook", {})
        data["facebook"]["page_name"] = page_name
        data["facebook"]["page_id"] = page_id.strip()
        data["facebook"]["access_token"] = access_token.strip()
        data["facebook"]["connected"] = bool(page_id.strip() and access_token.strip())
        save_json(data, self.accounts_file)
        return data["facebook"]

    def save_webhook_account(self, name: str, url: str, secret_token: str = "") -> Dict[str, Any]:
        data = self.get_all_accounts()
        data.setdefault("webhook", {})
        data["webhook"]["name"] = name
        data["webhook"]["url"] = url.strip()
        data["webhook"]["secret_token"] = secret_token.strip()
        data["webhook"]["connected"] = bool(url.strip())
        save_json(data, self.accounts_file)
        return data["webhook"]

    def save_ai_keys(self, groq_key: str = "", gemini_key: str = "", pexels_key: str = "") -> Dict[str, Any]:
        data = self.get_all_accounts()
        data.setdefault("ai_engines", {})
        if groq_key is not None:
            data["ai_engines"]["groq_api_key"] = groq_key.strip()
        if gemini_key is not None:
            data["ai_engines"]["gemini_api_key"] = gemini_key.strip()
        if pexels_key is not None:
            data["ai_engines"]["pexels_api_key"] = pexels_key.strip()
        save_json(data, self.accounts_file)
        return data["ai_engines"]

    def test_facebook(self, page_id: str, access_token: str) -> Dict[str, Any]:
        """Tests Facebook Graph API token against page."""
        if not page_id or not access_token:
            return {"success": False, "error": "Missing Page ID or Access Token."}
        try:
            url = f"https://graph.facebook.com/v19.0/{page_id}?fields=id,name,fan_count&access_token={access_token}"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                res = r.json()
                return {"success": True, "page_name": res.get("name", "Connected Page"), "fan_count": res.get("fan_count", 0)}
            else:
                return {"success": False, "error": r.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def test_webhook(self, url: str, secret: str = "") -> Dict[str, Any]:
        """Sends a test ping to custom Webhook endpoint."""
        if not url:
            return {"success": False, "error": "Webhook URL is empty."}
        try:
            headers = {"Content-Type": "application/json"}
            if secret:
                headers["Authorization"] = f"Bearer {secret}"
            payload = {"event": "ping", "message": "AI Content Factory Pro connection test", "timestamp": int(requests.utils.time.time())}
            r = requests.post(url, json=payload, headers=headers, timeout=10)
            return {"success": r.status_code in [200, 201, 202, 204], "status_code": r.status_code, "response": r.text[:200]}
        except Exception as e:
            return {"success": False, "error": str(e)}
