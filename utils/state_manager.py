"""
Session State and Workspace Manager for AI Content Factory SaaS.
Enables seamless cross-tab data flow between Research, Scripting, Audio, Visuals, and Publishing.
"""

from typing import Dict, Any, Optional
import streamlit as st
from config import DEFAULT_VOICE, DEFAULT_ORIENTATION, DEFAULT_RESOLUTION


def init_session_state():
    """Initializes global workspace state variables in Streamlit session."""
    defaults = {
        "workspace_topic": "",
        "workspace_niche": "tech",
        "workspace_content_type": "shorts",
        "workspace_script_data": None,
        "workspace_voice": DEFAULT_VOICE,
        "workspace_audio_res": None,
        "workspace_thumbnail_variants": [],
        "workspace_seo_data": None,
        "latest_production_result": None,
        "active_preset_key": "viral_shorts",
        "diagnostics_results": {}
    }
    
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def set_active_topic(topic: str, niche: str = "tech", content_type: str = "shorts"):
    """Sets active topic across all studio tabs."""
    st.session_state["workspace_topic"] = topic
    st.session_state["workspace_niche"] = niche
    st.session_state["workspace_content_type"] = content_type


def set_active_script(script_data: Dict[str, Any]):
    """Stores generated script in workspace state."""
    st.session_state["workspace_script_data"] = script_data
    if script_data.get("title"):
        st.session_state["workspace_topic"] = script_data.get("title")


def get_workspace_topic() -> str:
    """Gets current active topic."""
    return st.session_state.get("workspace_topic", "")
