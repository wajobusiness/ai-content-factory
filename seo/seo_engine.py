"""
AI Content Factory - SEO Engine
Optimizes video titles, descriptions, chapters, tags, and click-through rates.
"""

import json
import re
from typing import Dict, Any, Optional

from config import GROQ_API_KEY, GROQ_MODEL, GEMINI_API_KEY, GEMINI_MODEL, DEFAULT_LLM_PROVIDER
from utils.helpers import logger


class SEOEngine:
    """Automates YouTube and social media SEO metadata generation."""

    def __init__(
        self,
        provider: Optional[str] = None,
        groq_api_key: Optional[str] = None,
        gemini_api_key: Optional[str] = None
    ):
        self.provider = (provider or DEFAULT_LLM_PROVIDER).lower()
        self.groq_api_key = groq_api_key or GROQ_API_KEY
        self.gemini_api_key = gemini_api_key or GEMINI_API_KEY

    def optimize_video_seo(
        self,
        topic: str,
        script_data: Optional[Dict[str, Any]] = None,
        target_niche: str = "technology"
    ) -> Dict[str, Any]:
        logger.info(f"Generating SEO metadata for topic '{topic}'...")

        if self.provider == "groq" and self.groq_api_key:
            res = self._generate_with_groq(topic, target_niche)
            if res:
                return res

        if self.gemini_api_key:
            res = self._generate_with_gemini(topic, target_niche)
            if res:
                return res

        return self._generate_fallback_seo(topic, script_data, target_niche)

    def _build_prompt(self, topic: str, target_niche: str) -> str:
        return f"""You are a master YouTube SEO strategist.
Generate an elite SEO package for a video on the topic: "{topic}" (Niche: {target_niche}).

Return ONLY a JSON object:
{{
  "best_title": "Primary high-CTR viral title (under 60 chars)",
  "alternative_titles": [
    "Curiosity Hook Title",
    "Listicle / How-to Title",
    "Dramatic Shock Title"
  ],
  "description": "Engaging SEO description with introduction, timestamps, and call to action",
  "tags": ["keyword 1", "keyword 2", "keyword 3", "keyword 4"],
  "hashtags": ["#Topic", "#Trending", "#Shorts"],
  "clickability_score": 94
}}
"""

    def _generate_with_groq(self, topic: str, target_niche: str) -> Optional[Dict[str, Any]]:
        try:
            from groq import Groq
            client = Groq(api_key=self.groq_api_key)
            prompt = self._build_prompt(topic, target_niche)

            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a YouTube SEO optimizer. Output valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                model=GROQ_MODEL,
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            raw = response.choices[0].message.content
            return json.loads(raw)
        except Exception as e:
            logger.warning(f"Groq SEO generation failed: {e}")
            return None

    def _generate_with_gemini(self, topic: str, target_niche: str) -> Optional[Dict[str, Any]]:
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel(GEMINI_MODEL)
            prompt = self._build_prompt(topic, target_niche)
            res = model.generate_content(prompt)
            raw_text = res.text.strip()
            raw_text = re.sub(r"^```json\s*", "", raw_text)
            raw_text = re.sub(r"\s*```$", "", raw_text)
            return json.loads(raw_text)
        except Exception as e:
            logger.warning(f"Gemini SEO generation failed: {e}")
            return None

    def _generate_fallback_seo(
        self,
        topic: str,
        script_data: Optional[Dict[str, Any]],
        target_niche: str
    ) -> Dict[str, Any]:
        clean_topic = topic.strip()
        best_title = f"{clean_topic} (Everything You Need To Know)"

        alt_titles = [
            f"Why {clean_topic} Will Change EVERYTHING",
            f"The Truth About {clean_topic} Nobody Told You",
            f"How To Master {clean_topic} in 2026"
        ]

        chapters_text = "⏱️ Timestamps:\n0:00 - Introduction\n"
        if script_data and "scenes" in script_data:
            accum_sec = 0
            for sc in script_data["scenes"]:
                dur = sc.get("duration_seconds", 8)
                section = sc.get("section", f"Scene {sc.get('scene_number', 1)}")
                mins = int(accum_sec // 60)
                secs = int(accum_sec % 60)
                chapters_text += f"{mins:02d}:{secs:02d} - {section}\n"
                accum_sec += dur

        desc = f"""In this video, we dive deep into {clean_topic}. Discover key insights, latest trends, and step-by-step breakdown.

{chapters_text}
🔔 Subscribe for more daily {target_niche} breakdowns and AI automation tutorials!
👍 Like and leave a comment below!

#ai #contentfactory #{target_niche.replace(' ', '')} #viral
"""

        words = [w.lower() for w in re.findall(r'\b\w{4,}\b', clean_topic)]
        tags = [clean_topic.lower(), target_niche.lower(), "tutorial", "guide 2026", "review", "explained"]
        tags.extend([f"{w} explained" for w in words])

        hashtags = [f"#{w.capitalize()}" for w in words[:3]] + ["#Trending", "#Education"]

        return {
            "best_title": best_title,
            "alternative_titles": alt_titles,
            "description": desc,
            "tags": list(dict.fromkeys(tags))[:15],
            "hashtags": hashtags[:5],
            "clickability_score": 92
        }
