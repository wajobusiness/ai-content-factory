"""
AI Content Factory - Script Generator
Generates high-retention video scripts broken down into structured scenes.
Supports Groq (Llama 3 70B), Google Gemini, and Smart Template Engine.
"""

import os
import json
import re
from typing import Dict, Any, List, Optional

from config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    DEFAULT_LLM_PROVIDER
)
from utils.helpers import logger


class ScriptGenerator:
    """Generates structured video scripts for various content types."""

    def __init__(
        self,
        provider: Optional[str] = None,
        groq_api_key: Optional[str] = None,
        gemini_api_key: Optional[str] = None
    ):
        self.provider = (provider or DEFAULT_LLM_PROVIDER).lower()
        self.groq_api_key = groq_api_key or GROQ_API_KEY
        self.gemini_api_key = gemini_api_key or GEMINI_API_KEY

    def generate_script(
        self,
        topic: str,
        content_type: str = "tech_review",
        target_duration: str = "60s",
        tone: str = "engaging",
        target_audience: str = "general"
    ) -> Dict[str, Any]:
        logger.info(f"Generating script for topic '{topic}' ({content_type}, {target_duration})...")

        if self.provider == "groq" and self.groq_api_key:
            script = self._generate_with_groq(topic, content_type, target_duration, tone, target_audience)
            if script:
                return script

        if (self.provider == "gemini" or self.gemini_api_key) and self.gemini_api_key:
            script = self._generate_with_gemini(topic, content_type, target_duration, tone, target_audience)
            if script:
                return script

        logger.info("Using smart template engine fallback for script generation.")
        return self._generate_fallback_script(topic, content_type, target_duration, tone)

    def _build_prompt(
        self,
        topic: str,
        content_type: str,
        target_duration: str,
        tone: str,
        target_audience: str
    ) -> str:
        return f"""You are an elite viral video creator and YouTube algorithm specialist.
Create a complete, high-retention video script for the following specifications:

Topic: {topic}
Content Type: {content_type}
Target Duration: {target_duration}
Tone: {tone}
Target Audience: {target_audience}

You must return ONLY a strict JSON object with no markdown fences, matching this structure:
{{
  "title": "A viral, high-CTR video title",
  "topic": "{topic}",
  "content_type": "{content_type}",
  "hook": "First 3-5 seconds high-retention hook",
  "estimated_duration_seconds": 60,
  "scenes": [
    {{
      "scene_number": 1,
      "section": "Hook",
      "narration": "Voiceover narration words for this scene. Keep it energetic and natural.",
      "visual_prompt": "Detailed AI image generation prompt for this scene (cinematic, 8k, detailed lighting)",
      "pexels_query": "2-3 keyword search term for stock footage",
      "on_screen_text": "Short punchy text overlay",
      "duration_seconds": 6
    }},
    {{
      "scene_number": 2,
      "section": "Core Problem",
      "narration": "Next part of voiceover.",
      "visual_prompt": "AI image prompt...",
      "pexels_query": "stock video query...",
      "on_screen_text": "Key phrase...",
      "duration_seconds": 10
    }},
    {{
      "scene_number": 3,
      "section": "Breakthrough",
      "narration": "Deep dive point...",
      "visual_prompt": "AI image prompt...",
      "pexels_query": "stock video query...",
      "on_screen_text": "Key phrase...",
      "duration_seconds": 15
    }},
    {{
      "scene_number": 4,
      "section": "Impact",
      "narration": "Surprising insight or resolution...",
      "visual_prompt": "AI image prompt...",
      "pexels_query": "stock video query...",
      "on_screen_text": "Key phrase...",
      "duration_seconds": 15
    }},
    {{
      "scene_number": 5,
      "section": "Call to Action",
      "narration": "Subscribe, like, and leave a comment below. See you in the next one!",
      "visual_prompt": "Call to action subscribe button with neon glow",
      "pexels_query": "technology subscribe",
      "on_screen_text": "Like & Follow for more!",
      "duration_seconds": 6
    }}
  ],
  "call_to_action": "Subscribe and comment your thoughts below!"
}}
"""

    def _generate_with_groq(self, topic: str, content_type: str, target_duration: str, tone: str, target_audience: str) -> Optional[Dict[str, Any]]:
        try:
            from groq import Groq
            client = Groq(api_key=self.groq_api_key)
            prompt = self._build_prompt(topic, content_type, target_duration, tone, target_audience)

            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a professional video script writer. Output valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                model=GROQ_MODEL,
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            raw_content = response.choices[0].message.content
            data = json.loads(raw_content)
            self._post_process_script(data)
            return data
        except Exception as e:
            logger.warning(f"Groq script generation failed: {e}")
            return None

    def _generate_with_gemini(self, topic: str, content_type: str, target_duration: str, tone: str, target_audience: str) -> Optional[Dict[str, Any]]:
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel(GEMINI_MODEL)
            prompt = self._build_prompt(topic, content_type, target_duration, tone, target_audience)

            response = model.generate_content(prompt)
            raw_text = response.text.strip()
            raw_text = re.sub(r"^```json\s*", "", raw_text)
            raw_text = re.sub(r"\s*```$", "", raw_text)
            data = json.loads(raw_text)
            self._post_process_script(data)
            return data
        except Exception as e:
            logger.warning(f"Gemini script generation failed: {e}")
            return None

    def _post_process_script(self, data: Dict[str, Any]):
        scenes = data.get("scenes", [])
        full_text_list = []
        for s in scenes:
            narration = s.get("narration", "").strip()
            if narration:
                full_text_list.append(narration)

        data["full_voiceover_text"] = " ".join(full_text_list)
        if not data.get("estimated_duration_seconds"):
            data["estimated_duration_seconds"] = sum(s.get("duration_seconds", 8) for s in scenes)

    def _generate_fallback_script(self, topic: str, content_type: str, target_duration: str, tone: str) -> Dict[str, Any]:
        templates = {
            "tech_review": {
                "title": f"Why Everyone Is Talking About {topic} Right Now",
                "hook": f"What if I told you {topic} is about to change everything we know?",
                "scenes": [
                    {
                        "scene_number": 1,
                        "section": "Hook",
                        "narration": f"What if I told you {topic} is about to change everything? Most people have no idea this is happening.",
                        "visual_prompt": f"Futuristic high tech concept of {topic}, glowing neon circuits, cinematic lighting, 8k render",
                        "pexels_query": "artificial intelligence computer technology",
                        "on_screen_text": "THIS CHANGES EVERYTHING",
                        "duration_seconds": 6
                    },
                    {
                        "scene_number": 2,
                        "section": "The Core Problem",
                        "narration": "For years, we have been stuck doing things the old, slow way. But the recent breakthrough has completely disrupted the status quo.",
                        "visual_prompt": "Dramatic digital transformation visualization, sleek server room, blue atmospheric light",
                        "pexels_query": "server data futuristic lab",
                        "on_screen_text": "THE PROBLEM SOLVED",
                        "duration_seconds": 8
                    },
                    {
                        "scene_number": 3,
                        "section": "Breakthrough Feature",
                        "narration": f"Here is what makes {topic} truly unbelievable. The efficiency and capability have jumped forward by years, leaving competitors scrambling.",
                        "visual_prompt": f"High tech holographic interface showing data visualization and progress for {topic}",
                        "pexels_query": "modern technology digital screen",
                        "on_screen_text": "THE BREAKTHROUGH",
                        "duration_seconds": 10
                    },
                    {
                        "scene_number": 4,
                        "section": "Future Impact",
                        "narration": "Whether you are a creator, developer, or enthusiast, adopting this now gives you an unfair advantage before the rest of the world catches on.",
                        "visual_prompt": "Cinematic visual of people working with future tools, ultra realistic, warm studio lighting",
                        "pexels_query": "innovation workspace success",
                        "on_screen_text": "YOUR ADVANTAGE",
                        "duration_seconds": 8
                    },
                    {
                        "scene_number": 5,
                        "section": "Call to Action",
                        "narration": "What do you think? Are you ready for this shift? Let me know in the comments and hit subscribe for daily tech insights!",
                        "visual_prompt": "Glowing 3D subscribe button and notification bell with particle effects",
                        "pexels_query": "subscribe social media button",
                        "on_screen_text": "SUBSCRIBE & COMMENT",
                        "duration_seconds": 6
                    }
                ]
            }
        }

        chosen = templates.get(content_type, templates["tech_review"])
        result = {
            "title": chosen["title"],
            "topic": topic,
            "content_type": content_type,
            "hook": chosen["hook"],
            "scenes": chosen["scenes"],
            "call_to_action": "Subscribe and comment below!"
        }
        self._post_process_script(result)
        return result
