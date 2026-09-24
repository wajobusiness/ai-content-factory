"""
Header and Dashboard Hero Components for AI Content Factory SaaS.
"""

import streamlit as st
from config import GROQ_API_KEY, GEMINI_API_KEY, PEXELS_API_KEY


def render_dashboard_header(
    title: str = "🚀 AI Content Factory Pro",
    subtitle: str = "Autonomous Enterprise Video & Media Production Engine",
    active_tab_badge: str = "Production Ready"
):
    """Renders a modern SaaS hero banner with title, badges, and status pills."""
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
        <div>
            <div class="saas-hero-header">{title}</div>
            <div class="saas-hero-sub">{subtitle}</div>
        </div>
        <div style="text-align: right;">
            <span class="kpi-badge badge-pro">✨ v2.5 Pro Edition</span>
            <span class="kpi-badge badge-success">● 100% Free Engine</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_api_status_sidebar():
    """Renders sleek API connectivity health pills in the sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.markdown("#### ⚡ Engine Health & APIs")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.markdown(f"**Groq Llama 3**")
        st.markdown(f"**Gemini 1.5**")
        st.markdown(f"**Edge-TTS**")
        st.markdown(f"**Pollinations**")
        st.markdown(f"**Pexels Stock**")
    with col2:
        st.markdown(f"{'🟢 Online' if GROQ_API_KEY else '⚪ Fallback'}")
        st.markdown(f"{'🟢 Online' if GEMINI_API_KEY else '⚪ Fallback'}")
        st.markdown(f"🟢 **Free**")
        st.markdown(f"🟢 **Free**")
        st.markdown(f"{'🟢 Online' if PEXELS_API_KEY else '⚪ AI Mode'}")
    
    st.sidebar.caption("🔒 All fallbacks are active with 0 hard dependencies.")
