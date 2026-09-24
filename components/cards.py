"""
Card, Metric, and Media Components for AI Content Factory SaaS.
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import streamlit as st


def render_metric_card(title: str, value: str, badge: str = "", badge_type: str = "success", subtext: str = ""):
    """Renders a modern glassmorphic SaaS KPI card."""
    badge_html = f'<span class="kpi-badge badge-{badge_type}">{badge}</span>' if badge else ""
    st.markdown(f"""
    <div class="saas-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span class="kpi-title">{title}</span>
            {badge_html}
        </div>
        <div class="kpi-value">{value}</div>
        {f'<div style="font-size: 0.8rem; color: #94A3B8; margin-top: 4px;">{subtext}</div>' if subtext else ''}
    </div>
    """, unsafe_allow_html=True)


def render_trend_card(trend: Dict[str, Any], index: int) -> bool:
    """Renders a viral trend signal card with score badge."""
    title = trend.get("title", "Untitled Trend")
    source = trend.get("source", "Web Signal")
    score = trend.get("viral_score", 85)
    category = trend.get("category", "General")
    
    score_color = "#10B981" if score >= 85 else ("#F59E0B" if score >= 70 else "#6366F1")
    
    st.markdown(f"""
    <div class="saas-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div style="font-size: 1.1rem; font-weight: 700; color: #F8FAFC;">🔥 {title}</div>
            <span class="kpi-badge" style="background: rgba(255,255,255,0.06); border: 1px solid {score_color}; color: {score_color}; font-size: 0.85rem;">
                ★ {score}/100
            </span>
        </div>
        <div style="display: flex; gap: 12px; margin-top: 8px; font-size: 0.82rem; color: #94A3B8;">
            <span><strong>Source:</strong> {source}</span>
            <span>•</span>
            <span><strong>Category:</strong> {category.capitalize()}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_scene_card(scene: Dict[str, Any], scene_num: int):
    """Renders an editable / expandable script scene card."""
    section = scene.get("section", f"Scene {scene_num}")
    duration = scene.get("duration_seconds", 8)
    narration = scene.get("narration", "")
    visual_prompt = scene.get("visual_prompt", "")
    on_screen_text = scene.get("on_screen_text", "")
    
    with st.expander(f"🎬 Scene {scene_num}: {section} (~{duration}s)", expanded=(scene_num <= 2)):
        st.markdown(f"**🗣️ Narration:** {narration}")
        st.markdown(f"**🎨 Visual Direction:** `{visual_prompt}`")
        if on_screen_text:
            st.markdown(f"**📺 On-Screen Overlay:** `{on_screen_text}`")
