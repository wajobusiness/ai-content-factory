"""
AI Content Factory - Trend Finder
Discovers viral trends from Google Trends, Reddit, Hacker News, and AI Trend Synthesizer.
"""

import random
from typing import List, Dict, Any, Optional
from utils.helpers import logger

try:
    import requests
except ImportError:
    requests = None

try:
    import feedparser
except ImportError:
    feedparser = None


class TrendFinder:
    """Discovers trending topics, news, and viral content ideas."""

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def get_google_trends(self, geo: str = "US") -> List[Dict[str, Any]]:
        if not feedparser:
            return self.get_curated_niche_trends("tech")
        url = f"https://trends.google.com/trending/rss?geo={geo}"
        trends = []
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:15]:
                title = entry.get("title", "").strip()
                approx_traffic = entry.get("ht_approx_traffic", "100K+")
                trends.append({
                    "title": title,
                    "source": "Google Trends",
                    "traffic": approx_traffic,
                    "summary": entry.get("description", ""),
                    "viral_score": random.randint(85, 98),
                    "category": "General Trending"
                })
        except Exception as e:
            logger.warning(f"Error fetching Google Trends: {e}")

        return trends

    def get_reddit_trends(self, subreddit: str = "technology", limit: int = 10) -> List[Dict[str, Any]]:
        if not requests:
            return self.get_curated_niche_trends(subreddit)
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
        trends = []
        try:
            res = requests.get(url, headers=self.headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                children = data.get("data", {}).get("children", [])
                for child in children:
                    post = child.get("data", {})
                    if post.get("stickied"):
                        continue
                    title = post.get("title", "").strip()
                    score = post.get("score", 0)
                    comments = post.get("num_comments", 0)
                    viral_score = min(99, int(70 + (score / 200) + (comments / 50)))

                    trends.append({
                        "title": title,
                        "source": f"Reddit (r/{subreddit})",
                        "score": score,
                        "comments": comments,
                        "link": post.get("url", ""),
                        "viral_score": max(75, viral_score),
                        "category": subreddit.capitalize()
                    })
        except Exception as e:
            logger.warning(f"Error fetching Reddit trends for r/{subreddit}: {e}")

        return trends

    def get_hackernews_trends(self, limit: int = 8) -> List[Dict[str, Any]]:
        if not requests:
            return []
        trends = []
        try:
            top_ids_res = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=8)
            if top_ids_res.status_code == 200:
                top_ids = top_ids_res.json()[:limit]
                for item_id in top_ids:
                    item_res = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json", timeout=5)
                    if item_res.status_code == 200:
                        item = item_res.json()
                        trends.append({
                            "title": item.get("title", ""),
                            "source": "Hacker News",
                            "score": item.get("score", 0),
                            "comments": item.get("descendants", 0),
                            "link": item.get("url", f"https://news.ycombinator.com/item?id={item_id}"),
                            "viral_score": random.randint(80, 95),
                            "category": "Tech & Startups"
                        })
        except Exception as e:
            logger.warning(f"Error fetching Hacker News trends: {e}")

        return trends

    def get_curated_niche_trends(self, niche: str = "tech") -> List[Dict[str, Any]]:
        niche_db = {
            "tech": [
                {"title": "Top 5 AI Tools That Will Replace Entire Teams in 2026", "score": "98K", "category": "AI & Tech"},
                {"title": "The Quantum Computing Breakthrough Nobody Is Talking About", "score": "84K", "category": "Future Tech"},
                {"title": "Why Python 3.14 Will Change Programming Forever", "score": "76K", "category": "Programming"},
                {"title": "Is Apple Silicon M5 Really 10x Faster?", "score": "92K", "category": "Hardware"},
                {"title": "The Dark Side of Humanoid Robots Entering Our Homes", "score": "89K", "category": "Robotics"}
            ],
            "finance": [
                {"title": "7 Passive Income Streams That Actually Work in 2026", "score": "120K", "category": "Passive Income"},
                {"title": "How The Top 1% Protect Their Wealth During Inflation", "score": "95K", "category": "Wealth Building"},
                {"title": "The Index Fund Strategy That Beats 90% of Hedge Funds", "score": "82K", "category": "Investing"},
                {"title": "Why Real Estate May Face A Massive Shift This Year", "score": "79K", "category": "Real Estate"}
            ],
            "motivation": [
                {"title": "Discipline Beats Motivation: The 2-Minute Rule Changed My Life", "score": "150K", "category": "Mindset"},
                {"title": "Stop Wasting Your 20s: 5 Hard Truths You Need To Hear", "score": "134K", "category": "Life Lessons"},
                {"title": "The Stoic Mindset For Overcoming Extreme Stress & Anxiety", "score": "112K", "category": "Philosophy"},
                {"title": "How To Reset Your Brain Dopamine In 7 Days", "score": "98K", "category": "Habits"}
            ],
            "mystery": [
                {"title": "The Bizarre Mystery of The Dyatlov Pass Incident Solved?", "score": "140K", "category": "Unexplained"},
                {"title": "5 Deep Ocean Discoveries That Terrified Scientists", "score": "165K", "category": "Exploration"},
                {"title": "The Lost City Beneath The Amazon Revealed By LIDAR", "score": "118K", "category": "Archaeology"}
            ],
            "cartoons": [
                {"title": "Detective Byte and The Missing Cyber Bone", "score": "65K", "category": "Animated Series"},
                {"title": "Luna The Space Cat: Journey to Kepler-452b", "score": "88K", "category": "Sci-Fi Cartoon"},
                {"title": "The Tiny Dragon Who Was Scared of Sparks", "score": "94K", "category": "Bedtime Tales"}
            ]
        }

        items = niche_db.get(niche.lower(), niche_db["tech"])
        results = []
        for item in items:
            results.append({
                "title": item["title"],
                "source": "Curated Trend Radar",
                "traffic": item["score"],
                "viral_score": random.randint(86, 99),
                "category": item["category"]
            })
        return results

    def discover_all(self, niche: str = "tech") -> List[Dict[str, Any]]:
        all_trends = []
        all_trends.extend(self.get_curated_niche_trends(niche))

        subreddit_map = {
            "tech": "technology",
            "finance": "personalfinance",
            "motivation": "getmotivated",
            "mystery": "unresolvedmysteries",
            "science": "science",
            "general": "todayilearned"
        }
        sub = subreddit_map.get(niche.lower(), "technology")
        all_trends.extend(self.get_reddit_trends(subreddit=sub, limit=4))
        all_trends.extend(self.get_google_trends()[:3])

        if niche.lower() in ["tech", "science", "general"]:
            all_trends.extend(self.get_hackernews_trends(limit=3))

        seen_titles = set()
        deduped = []
        for t in all_trends:
            clean_title = t.get("title", "").strip()
            if clean_title and clean_title.lower() not in seen_titles:
                seen_titles.add(clean_title.lower())
                deduped.append(t)

        deduped.sort(key=lambda x: x.get("viral_score", 0), reverse=True)
        return deduped

