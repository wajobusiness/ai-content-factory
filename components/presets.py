"""
Production Presets and Templates for AI Content Factory SaaS.
"""

from typing import Dict, Any, List

PRODUCTION_PRESETS: Dict[str, Dict[str, Any]] = {
    "viral_shorts": {
        "name": "📱 TikTok & Shorts Viral Hook (60s)",
        "badge": "Highest Reach",
        "description": "Fast-paced vertical video designed for maximum retention, bold captions, and rapid scene cuts.",
        "niche": "tech",
        "content_type": "shorts",
        "orientation": "vertical",
        "resolution": "1080p",
        "duration": "60s",
        "voice": "en-US-GuyNeural",
        "style": "cyberpunk"
    },
    "tech_documentary": {
        "name": "🧠 Deep-Dive Tech Documentary (3m)",
        "badge": "High CPM",
        "description": "Widescreen cinematic explainer with rich narration, authoritative tone, and 8K visual sequences.",
        "niche": "tech",
        "content_type": "tech_review",
        "orientation": "landscape",
        "resolution": "1080p",
        "duration": "2m",
        "voice": "en-US-ChristopherNeural",
        "style": "cinematic"
    },
    "finance_wealth": {
        "name": "💰 Finance & Wealth Masterclass",
        "badge": "Top Monetization",
        "description": "Engaging breakdown of passive income, crypto, and stock market strategies with clear takeaways.",
        "niche": "finance",
        "content_type": "educational",
        "orientation": "landscape",
        "resolution": "1080p",
        "duration": "60s",
        "voice": "en-US-AriaNeural",
        "style": "photorealistic"
    },
    "motivational_speech": {
        "name": "🔥 Epic Discipline & Motivation",
        "badge": "Viral Engagement",
        "description": "Inspiring, hard-hitting motivational quotes paired with intense cinematic art and ambient score.",
        "niche": "motivation",
        "content_type": "motivational",
        "orientation": "vertical",
        "resolution": "1080p",
        "duration": "60s",
        "voice": "en-US-GuyNeural",
        "style": "cinematic"
    },
    "cartoon_tale": {
        "name": "🎭 Animated Cartoon Story",
        "badge": "Family Friendly",
        "description": "Character-driven 3D cartoon story with playful dialogue, speech bubbles, and charming soundscapes.",
        "niche": "cartoons",
        "content_type": "cartoon_series",
        "orientation": "landscape",
        "resolution": "720p",
        "duration": "60s",
        "voice": "en-US-EricNeural",
        "style": "3d_cartoon"
    },
    "news_flash": {
        "name": "⚡ Daily AI & Tech News Flash",
        "badge": "Trending Daily",
        "description": "Rapid-fire digest of the top breaking headlines, product launches, and scientific discoveries.",
        "niche": "tech",
        "content_type": "news_update",
        "orientation": "landscape",
        "resolution": "1080p",
        "duration": "60s",
        "voice": "en-GB-RyanNeural",
        "style": "digital_art"
    }
}


def get_preset_list() -> List[str]:
    """Returns formatted list of preset names for selectboxes."""
    return list(PRODUCTION_PRESETS.keys())


def get_preset(key: str) -> Dict[str, Any]:
    """Retrieves preset dictionary by key with fallback."""
    return PRODUCTION_PRESETS.get(key, PRODUCTION_PRESETS["viral_shorts"])
