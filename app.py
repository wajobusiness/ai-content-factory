"""
AI Content Factory Pro - Enterprise SaaS Web Dashboard
Interactive UI for automated video generation, trend research, voiceover, thumbnails, connected accounts, and Post API.
"""

import os
import sys
import time
import json
from pathlib import Path
import streamlit as st

# Add root folder to sys.path
ROOT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(ROOT_DIR))

from config import (
    AVAILABLE_VOICES,
    DEFAULT_VOICE,
    OUTPUT_DIR,
    TEMP_DIR,
    GROQ_API_KEY,
    GEMINI_API_KEY,
    PEXELS_API_KEY
)
from components.theme import inject_custom_theme
from components.header import render_dashboard_header, render_api_status_sidebar
from components.cards import render_metric_card, render_trend_card, render_scene_card
from components.stepper import render_stepper
from components.presets import PRODUCTION_PRESETS, get_preset
from utils.state_manager import init_session_state, set_active_topic, set_active_script, get_workspace_topic
from utils.bundle_exporter import create_asset_bundle_zip
from utils.diagnostics import run_system_diagnostics
from research.trend_finder import TrendFinder
from content.script_generator import ScriptGenerator
from content.voiceover_gen import VoiceoverGenerator
from content.ai_image_gen import AIImageGenerator
from content.thumbnail_maker import ThumbnailMaker
from content.cartoon_studio import CartoonStudio
from seo.seo_engine import SEOEngine
from platforms.account_manager import AccountManager
from platforms.youtube_uploader import YouTubeUploader
from platforms.facebook_publisher import FacebookPublisher
from auto_scheduler import ContentPipeline
from utils.helpers import load_json
from utils.task_runner import task_manager
from components.task_banner import render_active_task_banner, render_sidebar_task_indicator

# Configure Streamlit page
st.set_page_config(
    page_title="AI Content Factory Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom SaaS CSS & Design System
inject_custom_theme()

# Initialize unified session state
init_session_state()

# Navigation & Branding
st.sidebar.markdown("""
<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px; padding: 4px;">
    <div style="background: linear-gradient(135deg, #6366F1, #EC4899); width: 38px; height: 38px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.25rem; font-weight: 800; color: white; box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);">⚡</div>
    <div>
        <div style="font-size: 1.2rem; font-weight: 800; color: #F8FAFC; letter-spacing: -0.02em;">ContentForge</div>
        <div style="font-size: 0.72rem; color: #A5B4FC; font-weight: 600;">Autonomous Media SaaS</div>
    </div>
</div>
""", unsafe_allow_html=True)

menu_options = [
    "🏠 Studio Hub (Home)",
    "🚀 One-Click Studio",
    "🔍 Trend Radar",
    "📝 AI Script Studio",
    "🎙️ Voiceover Studio",
    "🎨 Visuals & A/B Thumbnails",
    "🎭 3D Cartoon Studio",
    "📈 Viral SEO Engine",
    "🔗 Connected Accounts & Post API",
    "📤 Social Publisher",
    "🗄️ Media Library & Diagnostics"
]

menu = st.sidebar.radio(
    "Navigation Menu",
    menu_options,
    index=0
)

# Render active workspace chip in sidebar if present
active_topic = get_workspace_topic()
if active_topic:
    st.sidebar.markdown(f"""
    <div style="background: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.25); border-radius: 8px; padding: 10px; margin-top: 10px;">
        <div style="font-size: 0.72rem; color: #A5B4FC; text-transform: uppercase; font-weight: 700;">Active Topic</div>
        <div style="font-size: 0.82rem; color: #F8FAFC; font-weight: 600; margin-top: 3px; word-break: break-word;">{active_topic[:42]}...</div>
    </div>
    """, unsafe_allow_html=True)

render_sidebar_task_indicator()
render_api_status_sidebar()

# Render global persistent task banner across all studio pages
render_active_task_banner()

# ==============================================================================
# TAB 0: STUDIO HUB (HOME PAGE)
# ==============================================================================
if menu == "🏠 Studio Hub (Home)":
    render_dashboard_header(
        title="🏠 Studio Hub & Launchpad",
        subtitle="Welcome to your AI Content Command Center. Build, schedule, and distribute high-retention content autonomously."
    )

    # Top KPI Metrics Row
    history_file = OUTPUT_DIR / "pipeline_history.json"
    records = load_json(history_file, default=[])
    total_videos = len(records)
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_metric_card("Total Productions", str(total_videos), badge="Active", badge_type="pro", subtext="Rendered videos")
    with m2:
        render_metric_card("Production Cost", "$0.00", badge="Free Tier", badge_type="success", subtext="100% Free stack")
    with m3:
        render_metric_card("Average Render", "~45s", badge="High Speed", badge_type="success", subtext="MoviePy + FFmpeg")
    with m4:
        acct_mgr = AccountManager()
        accts = acct_mgr.get_all_accounts()
        connected_count = sum(1 for k in ["youtube", "facebook", "webhook"] if accts.get(k, {}).get("connected"))
        render_metric_card("Connected Accounts", f"{connected_count}/3 Active", badge="Ready", badge_type="pro", subtext="YouTube, FB, Webhooks")

    st.markdown("---")
    st.markdown("### ⚡ Quick Studio Launchpad")
    st.markdown("Jump directly into any production studio or trigger an end-to-end automated workflow:")

    c_l1, c_l2, c_l3 = st.columns(3)

    with c_l1:
        st.markdown("""
        <div class="launchpad-card">
            <div class="launchpad-icon" style="background: rgba(99, 102, 241, 0.15); color: #818CF8;">🚀</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #F8FAFC;">One-Click Studio</div>
            <div style="font-size: 0.85rem; color: #94A3B8; margin: 6px 0 14px 0;">Generate an entire multi-scene HD video with voiceover, A/B thumbnails & SEO in 60s.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch One-Click Studio ➔", key="launch_one_click", use_container_width=True, type="primary"):
            st.session_state["nav_override"] = "🚀 One-Click Studio"
            st.info("Select '🚀 One-Click Studio' from the sidebar menu to begin.")

    with c_l2:
        st.markdown("""
        <div class="launchpad-card">
            <div class="launchpad-icon" style="background: rgba(236, 72, 153, 0.15); color: #F472B6;">🔍</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #F8FAFC;">Viral Trend Radar</div>
            <div style="font-size: 0.85rem; color: #94A3B8; margin: 6px 0 14px 0;">Scan Google Trends, Reddit, and Hacker News for viral topics scored by momentum.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Scan Trends ➔", key="launch_trends", use_container_width=True):
            st.info("Select '🔍 Trend Radar' from the sidebar menu to explore.")

    with c_l3:
        st.markdown("""
        <div class="launchpad-card">
            <div class="launchpad-icon" style="background: rgba(16, 185, 129, 0.15); color: #34D399;">🔗</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #F8FAFC;">Post API & Accounts</div>
            <div style="font-size: 0.85rem; color: #94A3B8; margin: 6px 0 14px 0;">Connect YouTube, Facebook & Webhooks, and test the programmatic Post API endpoint.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Manage Accounts & API ➔", key="launch_accounts", use_container_width=True):
            st.info("Select '🔗 Connected Accounts & Post API' from the sidebar menu.")

    c_l4, c_l5, c_l6 = st.columns(3)

    with c_l4:
        st.markdown("""
        <div class="launchpad-card">
            <div class="launchpad-icon" style="background: rgba(245, 158, 11, 0.15); color: #FBBF24;">🎙️</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #F8FAFC;">Voiceover Studio</div>
            <div style="font-size: 0.85rem; color: #94A3B8; margin: 6px 0 14px 0;">100% Free natural human voice synthesis with pitch/speed controls and synced SRT.</div>
        </div>
        """, unsafe_allow_html=True)

    with c_l5:
        st.markdown("""
        <div class="launchpad-card">
            <div class="launchpad-icon" style="background: rgba(168, 85, 247, 0.15); color: #C084FC;">🎨</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #F8FAFC;">A/B Thumbnail Maker</div>
            <div style="font-size: 0.85rem; color: #94A3B8; margin: 6px 0 14px 0;">Generate 3 high-converting thumbnail variants simultaneously for CTR split testing.</div>
        </div>
        """, unsafe_allow_html=True)

    with c_l6:
        st.markdown("""
        <div class="launchpad-card">
            <div class="launchpad-icon" style="background: rgba(59, 130, 246, 0.15); color: #60A5FA;">🎭</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #F8FAFC;">3D Cartoon Studio</div>
            <div style="font-size: 0.85rem; color: #94A3B8; margin: 6px 0 14px 0;">Create animated stories with character consistency, speech bubbles, and soundscapes.</div>
        </div>
        """, unsafe_allow_html=True)

    # Active Project Status Banner
    if active_topic:
        st.markdown("---")
        st.markdown("### 📌 Active Workspace Project")
        st.info(f"**Current Topic:** {active_topic}\n\nYou can refine the script in **📝 AI Script Studio**, generate custom audio in **🎙️ Voiceover Studio**, or render in **🚀 One-Click Studio**.")


# ==============================================================================
# TAB 1: ONE-CLICK PRODUCTION STUDIO
# ==============================================================================
elif menu == "🚀 One-Click Studio":
    render_dashboard_header(
        title="🚀 Autonomous Video Studio",
        subtitle="End-to-end multi-scene video, AI voiceover, A/B thumbnails & SEO package in 60 seconds."
    )

    # Production Preset Selector
    st.markdown("##### ⚡ Choose a Production Preset")
    preset_keys = list(PRODUCTION_PRESETS.keys())
    preset_cols = st.columns(len(preset_keys))
    
    for idx, p_key in enumerate(preset_keys):
        p_info = PRODUCTION_PRESETS[p_key]
        with preset_cols[idx]:
            is_active = (st.session_state.get("active_preset_key") == p_key)
            btn_label = f"{p_info['name'].split()[0]} {p_info['name'].split()[1]}"
            if st.button(btn_label, key=f"preset_btn_{p_key}", use_container_width=True, type="primary" if is_active else "secondary"):
                st.session_state["active_preset_key"] = p_key
                st.rerun()

    active_preset = get_preset(st.session_state.get("active_preset_key", "viral_shorts"))

    st.markdown(f"""
    <div style="background: rgba(99, 102, 241, 0.06); border: 1px solid rgba(99, 102, 241, 0.2); border-radius: 10px; padding: 10px 16px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center;">
        <div>
            <strong style="color: #F8FAFC;">Active Template:</strong> <span style="color: #A5B4FC;">{active_preset['name']}</span>
            <span style="color: #94A3B8; font-size: 0.85rem; margin-left: 8px;">• {active_preset['description']}</span>
        </div>
        <span class="kpi-badge badge-pro">{active_preset['badge']}</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.1, 0.9])

    with col1:
        st.markdown("#### ⚙️ Video Parameters")
        
        prefilled_topic = st.session_state.get("workspace_topic", "")
        topic_input = st.text_input(
            "Video Topic / Keyword (leave blank to auto-detect viral trend)",
            value=prefilled_topic,
            placeholder="e.g. 5 AI Inventions in 2026 That Feel Like Pure Magic"
        )

        c_niche, c_style = st.columns(2)
        with c_niche:
            niche_list = ["tech", "finance", "motivation", "mystery", "cartoons", "science", "general"]
            niche_idx = niche_list.index(active_preset["niche"]) if active_preset["niche"] in niche_list else 0
            niche_option = st.selectbox("Content Niche", niche_list, index=niche_idx)
        with c_style:
            style_list = ["shorts", "tech_review", "motivational", "news_update", "cartoon_series", "educational", "mystery"]
            style_idx = style_list.index(active_preset["content_type"]) if active_preset["content_type"] in style_list else 0
            content_type = st.selectbox("Content Format", style_list, index=style_idx)

        c_orient, c_voice = st.columns(2)
        with c_orient:
            orient_list = ["vertical", "landscape", "square"]
            orient_idx = orient_list.index(active_preset["orientation"]) if active_preset["orientation"] in orient_list else 0
            orientation = st.selectbox("Orientation", orient_list, index=orient_idx)
        with c_voice:
            voice_keys = list(AVAILABLE_VOICES.keys())
            matched_voice_idx = 0
            for v_idx, v_k in enumerate(voice_keys):
                if AVAILABLE_VOICES[v_k] == active_preset["voice"]:
                    matched_voice_idx = v_idx
                    break
            voice_choice = st.selectbox("Voice Talent", voice_keys, index=matched_voice_idx)
            selected_voice = AVAILABLE_VOICES[voice_choice]

        c_res, c_upload = st.columns(2)
        with c_res:
            resolution = st.selectbox("Resolution", ["1080p", "720p"], index=0 if active_preset["resolution"] == "1080p" else 1)
        with c_upload:
            enable_upload = st.checkbox("Simulate Social Publishing", value=True)

        generate_btn = st.button("🚀 Render Complete Content Package", type="primary", use_container_width=True)

    with col2:
        st.markdown("#### 📊 Studio KPIs & Pipeline")
        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            render_metric_card("Cost", "$0.00", badge="Free Tier", badge_type="success", subtext="0 API fees")
        with kpi2:
            render_metric_card("Render Engine", "MoviePy Pro", badge="Fast Mode", badge_type="pro", subtext="Ken Burns + Ducking")
        with kpi3:
            render_metric_card("Voice Model", "Neural Edge", badge="HD Audio", badge_type="success", subtext="Sync Subtitles")

        st.markdown("""
        <div class="saas-card" style="margin-top: 10px;">
            <div style="font-weight: 700; color: #F8FAFC; margin-bottom: 6px;">⚡ Autonomous Pipeline Lifecycle:</div>
            <div style="font-size: 0.85rem; color: #94A3B8; line-height: 1.6;">
                1. 🔍 <strong>Trend & Script</strong>: Fetches viral signals and crafts retention hooks<br/>
                2. 🎙️ <strong>Neural Audio</strong>: Synthesizes high-fidelity speech and word-level SRT<br/>
                3. 🎨 <strong>Visual Assembly</strong>: Generates cinematic scenes & dynamic motion effects<br/>
                4. 🖼️ <strong>A/B Thumbnails</strong>: Builds 3 high-CTR thumbnail variants for testing<br/>
                5. 📈 <strong>SEO & Metadata</strong>: Generates viral title hooks, descriptions, and tags
            </div>
        </div>
        """, unsafe_allow_html=True)

    if generate_btn:
        active_t = task_manager.get_active_task()
        if active_t and active_t.status == "running":
            st.warning("⚠️ A production job is already active in the background. Stop it or wait for it to finish.")
        else:
            pipeline = ContentPipeline()
            task_title = topic_input.strip() if topic_input.strip() else f"Auto-{niche_option.capitalize()}-Video"
            task_manager.start_pipeline_task(
                task_name=f"Produce: {task_title[:32]}",
                target_fn=pipeline.run_full_pipeline,
                kwargs={
                    "topic": topic_input.strip() if topic_input.strip() else None,
                    "niche": niche_option,
                    "content_type": content_type,
                    "voice": selected_voice,
                    "orientation": orientation,
                    "resolution": resolution,
                    "enable_upload": enable_upload,
                    "dry_run": True
                }
            )
            st.session_state["workspace_topic"] = task_title
            st.rerun()

    # Live In-Studio Progress Monitor if Task is Running
    active_t = task_manager.get_active_task()
    if active_t and active_t.status == "running":
        summary = active_t.get_summary()
        st.markdown("---")
        st.markdown("### ⚡ Live Autonomous Production in Progress")
        st.markdown(f"**Current Phase:** `{summary['current_step']}` | **Elapsed:** {summary['elapsed_seconds']}s")
        st.progress(summary["progress"])
        
        with st.expander("📜 Live Worker Execution Logs", expanded=True):
            for log_line in summary["logs"][-6:]:
                st.code(log_line, language="text")

        c_stop_in_page, _ = st.columns([1, 3])
        with c_stop_in_page:
            if st.button("🛑 Stop Autonomous Production", key="btn_stop_in_studio_page", type="primary", use_container_width=True):
                task_manager.cancel_active_task()
                st.rerun()

        # Streamlit auto-refresh while active
        time.sleep(1.2)
        st.rerun()

    # Display Latest Production Results
    latest = st.session_state.get("latest_production_result")
    if isinstance(latest, dict) and latest.get("video_path") and (not active_t or active_t.status != "running"):
        st.markdown("---")
        st.markdown("### 📦 Production Deliverables & Assets")

        zip_buffer = create_asset_bundle_zip(latest)
        st.download_button(
            label="⚡ Download Complete Production Bundle (.ZIP with Video, Audio, Thumbnails, SRT & SEO)",
            data=zip_buffer,
            file_name=f"content_bundle_{int(time.time())}.zip",
            mime="application/zip",
            type="primary",
            use_container_width=True
        )

        r_col1, r_col2 = st.columns([1, 1])

        with r_col1:
            st.markdown("#### 🎬 Final HD Video")
            if latest.get("video_path") and os.path.exists(latest.get("video_path")):
                st.video(latest.get("video_path"))
                with open(latest.get("video_path"), "rb") as vf:
                    st.download_button("⬇️ Download Video (MP4)", vf, file_name=os.path.basename(latest.get("video_path")), mime="video/mp4", use_container_width=True)

            st.markdown("#### 🖼️ Primary High-CTR Thumbnail")
            if latest.get("thumbnail_path") and os.path.exists(latest.get("thumbnail_path")):
                st.image(latest.get("thumbnail_path"), use_container_width=True)
                with open(latest.get("thumbnail_path"), "rb") as tf:
                    st.download_button("⬇️ Download Primary Thumbnail (JPG)", tf, file_name=os.path.basename(latest.get("thumbnail_path")), mime="image/jpeg", use_container_width=True)

        with r_col2:
            st.markdown("#### 🎙️ Master Audio & Subtitles")
            if latest.get("audio_path") and os.path.exists(latest.get("audio_path")):
                st.audio(latest.get("audio_path"))
            if latest.get("srt_path") and os.path.exists(latest.get("srt_path")):
                with open(latest.get("srt_path"), "r", encoding="utf-8") as sf:
                    st.download_button("⬇️ Download Subtitles (.SRT)", sf.read(), file_name=os.path.basename(latest.get("srt_path")), mime="text/plain", use_container_width=True)

            st.markdown("#### 📈 Viral SEO Metadata")
            seo = latest.get("seo", {})
            st.text_input("Best Title", value=seo.get("best_title", latest.get("title", "")))
            st.text_area("Optimized Description", value=seo.get("description", ""), height=130)
            st.text_input("Recommended Tags", value=", ".join(seo.get("tags", [])))
            st.text_input("Social Hashtags", value=" ".join(seo.get("hashtags", [])))


# ==============================================================================
# TAB 2: TREND RADAR
# ==============================================================================
elif menu == "🔍 Trend Radar":
    render_dashboard_header(
        title="🔍 Viral Trend Radar",
        subtitle="Real-time predictive trend intelligence aggregated from Google Trends, Reddit, and Hacker News."
    )

    c_filter, c_btn = st.columns([3, 1])
    with c_filter:
        niche_filter = st.selectbox("Select Target Niche", ["tech", "finance", "motivation", "mystery", "cartoons", "science", "general"])
    with c_btn:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        scan_btn = st.button("🔄 Scan Viral Signals", type="primary", use_container_width=True)

    if scan_btn or "cached_trends" not in st.session_state:
        finder = TrendFinder()
        with st.spinner("Analyzing viral search volume & social momentum..."):
            trends = finder.discover_all(niche=niche_filter)
            st.session_state["cached_trends"] = trends

    trends = st.session_state.get("cached_trends", [])
    st.markdown(f"##### 🔥 Found {len(trends)} High-Velocity Topics for **{niche_filter.capitalize()}**:")

    for idx, t in enumerate(trends):
        render_trend_card(t, idx)
        c_use1, c_use2 = st.columns([1, 4])
        with c_use1:
            if st.button(f"⚡ Use Topic", key=f"use_topic_{idx}", use_container_width=True):
                set_active_topic(t.get("title", ""), niche=niche_filter)
                st.success(f"Selected: '{t.get('title')}'! Go to One-Click Studio to render.")


# ==============================================================================
# TAB 3: AI SCRIPT STUDIO
# ==============================================================================
elif menu == "📝 AI Script Studio":
    render_dashboard_header(
        title="📝 AI Script & Story Studio",
        subtitle="Generate scene-by-scene high-retention video scripts with retention hooks and visual directions."
    )

    current_top = get_workspace_topic()
    s_topic = st.text_input("Video Topic / Premise", value=current_top if current_top else "Why Quantum Computing Will Disrupt Cryptography in 2026")

    c1, c2, c3 = st.columns(3)
    with c1:
        s_type = st.selectbox("Content Archetype", ["tech_review", "news_update", "motivational", "educational", "mystery", "shorts"])
    with c2:
        s_duration = st.select_slider("Target Duration", options=["30s", "60s", "2m", "5m"], value="60s")
    with c3:
        s_tone = st.selectbox("Script Tone", ["Engaging & Fast", "Cinematic & Serious", "Humorous & Casual", "Authoritative Expert"])

    if st.button("✍️ Generate Multi-Scene Script", type="primary", use_container_width=True):
        script_gen = ScriptGenerator()
        with st.spinner("Writing retention-optimized script and visual prompts..."):
            script_data = script_gen.generate_script(topic=s_topic, content_type=s_type, target_duration=s_duration)
        
        set_active_script(script_data)
        st.session_state["workspace_script_data"] = script_data

    saved_script = st.session_state.get("workspace_script_data")
    if saved_script:
        st.markdown("---")
        st.markdown(f"### 📌 {saved_script.get('title', 'Video Script')}")
        st.info(f"**Retention Hook:** {saved_script.get('hook', 'N/A')}")

        for idx, sc in enumerate(saved_script.get("scenes", [])):
            render_scene_card(sc, idx + 1)

        st.markdown("#### 📜 Full Voiceover Narration")
        st.text_area("Full Narration Text", value=saved_script.get("full_voiceover_text", ""), height=150)


# ==============================================================================
# TAB 4: VOICEOVER STUDIO
# ==============================================================================
elif menu == "🎙️ Voiceover Studio":
    render_dashboard_header(
        title="🎙️ Neural Voiceover Studio",
        subtitle="100% Free natural human voice synthesis powered by Microsoft Neural Edge-TTS."
    )

    prefilled_text = ""
    if st.session_state.get("workspace_script_data"):
        prefilled_text = st.session_state["workspace_script_data"].get("full_voiceover_text", "")

    text_input = st.text_area(
        "Narration Script",
        value=prefilled_text if prefilled_text else "Welcome back! In today's video, we are breaking down the biggest breakthrough in artificial intelligence. Don't forget to like and subscribe!",
        height=150
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        voice_name = st.selectbox("Select Voice Character", list(AVAILABLE_VOICES.keys()))
        chosen_voice = AVAILABLE_VOICES[voice_name]
    with c2:
        speed_rate = st.select_slider("Speed Rate", options=["-20%", "-10%", "+0%", "+10%", "+20%"], value="+0%")
    with c3:
        pitch_val = st.select_slider("Pitch Adjust", options=["-10Hz", "-5Hz", "+0Hz", "+5Hz", "+10Hz"], value="+0Hz")

    if st.button("🔊 Synthesize Master Audio & Subtitles", type="primary", use_container_width=True):
        vg = VoiceoverGenerator()
        with st.spinner("Synthesizing neural voiceover & generating synced SRT..."):
            v_res = vg.generate(text=text_input, voice=chosen_voice, rate=speed_rate, pitch=pitch_val)
        
        st.session_state["workspace_audio_res"] = v_res
        st.success(f"Generated {v_res.get('duration')}s voiceover!")

    audio_res = st.session_state.get("workspace_audio_res")
    if audio_res:
        st.audio(audio_res.get("audio_path"))
        c_dl1, c_dl2 = st.columns(2)
        with c_dl1:
            if audio_res.get("audio_path") and os.path.exists(audio_res.get("audio_path")):
                with open(audio_res.get("audio_path"), "rb") as af:
                    st.download_button("⬇️ Download MP3 Audio", af, file_name=os.path.basename(audio_res.get("audio_path")), mime="audio/mpeg", use_container_width=True)
        with c_dl2:
            if audio_res.get("srt_path") and os.path.exists(audio_res.get("srt_path")):
                with open(audio_res.get("srt_path"), "r", encoding="utf-8") as sf:
                    st.download_button("⬇️ Download Subtitles (.SRT)", sf.read(), file_name=os.path.basename(audio_res.get("srt_path")), mime="text/plain", use_container_width=True)


# ==============================================================================
# TAB 5: VISUALS & A/B THUMBNAILS
# ==============================================================================
elif menu == "🎨 Visuals & A/B Thumbnails":
    render_dashboard_header(
        title="🎨 Visuals & A/B Thumbnail Studio",
        subtitle="Generate 8K AI artwork and A/B test high-converting thumbnail variants."
    )

    tab_vis, tab_thumb = st.tabs(["🖼️ AI Visual Generator", "🏷️ A/B/C Thumbnail Split Tester"])

    with tab_vis:
        img_prompt = st.text_input("Visual Prompt", value="Futuristic robotic scientist creating glowing holographic interface, ultra detailed")
        c1, c2 = st.columns(2)
        with c1:
            style = st.selectbox("Artistic Style", ["cinematic", "3d_cartoon", "anime", "cyberpunk", "photorealistic", "digital_art"])
        with c2:
            dim_choice = st.selectbox("Aspect Ratio", ["Landscape 16:9 (1280x720)", "Vertical 9:16 (720x1280)", "Square 1:1 (1024x1024)"])

        if st.button("✨ Generate AI Artwork", type="primary", use_container_width=True):
            im_gen = AIImageGenerator()
            w, h = (1280, 720) if "Landscape" in dim_choice else ((720, 1280) if "Vertical" in dim_choice else (1024, 1024))
            with st.spinner("Generating artwork via Pollinations AI..."):
                img_p = im_gen.generate_image(prompt=img_prompt, style=style, width=w, height=h)
            st.image(img_p, caption=f"Generated Image ({style})", use_container_width=True)

    with tab_thumb:
        st.markdown("##### 🧪 A/B/C Thumbnail Split Testing Generator")
        st.caption("Generates 3 distinct colorway and badge variations simultaneously to maximize Click-Through-Rate (CTR).")

        t_title = st.text_input("Headline Title", value=get_workspace_topic()[:35] if get_workspace_topic() else "THIS CHANGES EVERYTHING!")
        t_bg_prompt = st.text_input("Background Visual Prompt", value="glowing cyberspace matrix network")

        if st.button("🎨 Generate 3 A/B/C Thumbnail Variants", type="primary", use_container_width=True):
            tm = ThumbnailMaker()
            with st.spinner("Designing 3 distinct high-converting thumbnail variations..."):
                variants = tm.create_thumbnail_variants(title=t_title, ai_prompt=t_bg_prompt)
                st.session_state["workspace_thumbnail_variants"] = variants

        t_variants = st.session_state.get("workspace_thumbnail_variants", [])
        if t_variants:
            v_cols = st.columns(len(t_variants))
            for idx, var in enumerate(t_variants):
                with v_cols[idx]:
                    st.markdown(f"**Variant {var['variant']}: {var['style']}**")
                    if os.path.exists(var["path"]):
                        st.image(var["path"], use_container_width=True)
                        with open(var["path"], "rb") as vf:
                            st.download_button(f"⬇️ Download Variant {var['variant']}", vf, file_name=os.path.basename(var["path"]), mime="image/jpeg", use_container_width=True)


# ==============================================================================
# TAB 6: CARTOON STUDIO
# ==============================================================================
elif menu == "🎭 3D Cartoon Studio":
    render_dashboard_header(
        title="🎭 3D Cartoon Story Studio",
        subtitle="Create animated character episodes with comic speech bubbles, whimsical narration, and soundscapes."
    )

    c_premise = st.text_input("Story Premise", value="The tiny dragon who was scared of sparks learns to light up the dark forest")
    c1, c2 = st.columns(2)
    with c1:
        c_name = st.text_input("Character Name", value="Pip the Dragon")
    with c2:
        c_desc = st.text_input("Character Appearance", value="a cute baby purple dragon with big green eyes and glowing wings")

    if st.button("🎬 Produce Animated Cartoon Episode", type="primary", use_container_width=True):
        cs = CartoonStudio()
        with st.spinner("Assembling cartoon characters, speech bubbles, and dialogue..."):
            ep = cs.create_cartoon_episode(
                premise=c_premise,
                character_name=c_name,
                character_description=c_desc
            )
        
        st.subheader(f"🌟 {ep.get('title')}")
        st.audio(ep.get("voiceover", {}).get("audio_path"))

        for sc in ep.get("scenes", []):
            st.image(sc.get("image_path"), caption=f"Scene {sc.get('scene_number')}: {sc.get('narration')}", use_container_width=True)


# ==============================================================================
# TAB 7: SEO ENGINE
# ==============================================================================
elif menu == "📈 Viral SEO Engine":
    render_dashboard_header(
        title="📈 Viral SEO & Metadata Optimizer",
        subtitle="Generate viral YouTube/TikTok titles, clickability-scored descriptions, and keyword tags."
    )

    current_top = get_workspace_topic()
    seo_topic = st.text_input("Topic for SEO Optimization", value=current_top if current_top else "Top 5 Passive Income Ideas for Beginners in 2026")
    seo_niche = st.selectbox("Niche Category", ["technology", "finance", "motivation", "health", "gaming", "education"])

    if st.button("🚀 Calculate SEO & Clickability Score", type="primary", use_container_width=True):
        engine = SEOEngine()
        with st.spinner("Calculating viral hooks and SEO score..."):
            res = engine.optimize_video_seo(topic=seo_topic, target_niche=seo_niche)
            st.session_state["workspace_seo_data"] = res

    seo_res = st.session_state.get("workspace_seo_data")
    if seo_res:
        k1, k2 = st.columns([1, 3])
        with k1:
            render_metric_card("Clickability Score", f"{seo_res.get('clickability_score', 94)}/100", badge="High CTR", badge_type="success")
        with k2:
            st.markdown("#### 🎯 Best High-CTR Title")
            st.code(seo_res.get("best_title"))

        st.markdown("#### 💡 Alternative Title Hooks")
        for alt in seo_res.get("alternative_titles", []):
            st.markdown(f"• **{alt}**")

        st.markdown("#### 📝 Algorithmic Description")
        st.text_area("Description Text", value=seo_res.get("description"), height=160)

        st.markdown("#### 🏷️ Keyword Tags")
        st.code(", ".join(seo_res.get("tags", [])))


# ==============================================================================
# TAB 8: CONNECTED ACCOUNTS & POST API
# ==============================================================================
elif menu == "🔗 Connected Accounts & Post API":
    render_dashboard_header(
        title="🔗 Connected Accounts & Post API",
        subtitle="Connect social media accounts, store API tokens, and access the automated HTTP Post API."
    )

    tab_accts, tab_api = st.tabs(["🔐 Connected Accounts & Keys", "⚡ Interactive Post API Sandbox & Docs"])

    acct_mgr = AccountManager()
    accts = acct_mgr.get_all_accounts()

    with tab_accts:
        st.markdown("### 📱 Social Publishing Accounts")
        st.caption("Link your YouTube channel, Facebook Page, or automated Webhooks to enable one-click publishing.")

        # YouTube Account
        with st.expander("▶️ YouTube Channel Integration", expanded=True):
            yt_data = accts.get("youtube", {})
            yt_name = st.text_input("Channel Label / Name", value=yt_data.get("channel_name", "My YouTube Channel"))
            yt_secrets = st.text_input("Client Secrets Path (JSON)", value=yt_data.get("client_secrets_path", ""))
            yt_token = st.text_input("Token Path (JSON)", value=yt_data.get("token_path", ""))
            
            c_yt1, c_yt2 = st.columns(2)
            with c_yt1:
                if st.button("💾 Save YouTube Account", type="primary"):
                    acct_mgr.save_youtube_account(channel_name=yt_name, client_secrets_path=yt_secrets, token_path=yt_token)
                    st.success("YouTube account configuration saved!")
            with c_yt2:
                yt_status = "🟢 Connected" if (os.path.exists(yt_token) or os.path.exists(yt_secrets)) else "⚪ Simulation Mode Ready"
                st.markdown(f"**Status:** {yt_status}")

        # Facebook Account
        with st.expander("📘 Facebook Page & Reels Integration", expanded=True):
            fb_data = accts.get("facebook", {})
            fb_name = st.text_input("Page Name / Label", value=fb_data.get("page_name", "My Facebook Page"))
            fb_page_id = st.text_input("Facebook Page ID", value=fb_data.get("page_id", ""))
            fb_token = st.text_input("Facebook Page Access Token", value=fb_data.get("access_token", ""), type="password")
            
            c_fb1, c_fb2 = st.columns(2)
            with c_fb1:
                if st.button("💾 Save Facebook Account", type="primary"):
                    acct_mgr.save_facebook_account(page_name=fb_name, page_id=fb_page_id, access_token=fb_token)
                    st.success("Facebook configuration saved!")
            with c_fb2:
                if st.button("🔍 Test Facebook Page Token"):
                    with st.spinner("Validating with Facebook Graph API..."):
                        t_res = acct_mgr.test_facebook(page_id=fb_page_id, access_token=fb_token)
                        if t_res.get("success"):
                            st.success(f"✅ Connected to '{t_res.get('page_name')}' ({t_res.get('fan_count')} followers)!")
                        else:
                            st.warning(f"Connection test: {t_res.get('error')}")

        # Webhook / TikTok / Zapier / Make.com
        with st.expander("🌐 Custom Automation Webhook (Make / Zapier / TikTok)", expanded=True):
            wh_data = accts.get("webhook", {})
            wh_name = st.text_input("Webhook Name", value=wh_data.get("name", "Make.com Content Automation"))
            wh_url = st.text_input("Webhook POST URL", value=wh_data.get("url", ""), placeholder="https://hook.eu1.make.com/xxxxxx")
            wh_secret = st.text_input("Bearer Secret / Token (optional)", value=wh_data.get("secret_token", ""), type="password")

            c_wh1, c_wh2 = st.columns(2)
            with c_wh1:
                if st.button("💾 Save Webhook Endpoint", type="primary"):
                    acct_mgr.save_webhook_account(name=wh_name, url=wh_url, secret_token=wh_secret)
                    st.success("Webhook endpoint saved!")
            with c_wh2:
                if st.button("📡 Send Test Ping"):
                    with st.spinner("Pinging Webhook..."):
                        p_res = acct_mgr.test_webhook(url=wh_url, secret=wh_secret)
                        if p_res.get("success"):
                            st.success(f"✅ Webhook ping successful (HTTP {p_res.get('status_code')})!")
                        else:
                            st.warning(f"Webhook test: {p_res.get('error')}")

        # Custom AI Engine Keys
        with st.expander("🔑 Custom AI Engine Keys (Optional)", expanded=False):
            ai_data = accts.get("ai_engines", {})
            k_groq = st.text_input("Groq API Key", value=ai_data.get("groq_api_key", GROQ_API_KEY), type="password")
            k_gemini = st.text_input("Gemini API Key", value=ai_data.get("gemini_api_key", GEMINI_API_KEY), type="password")
            k_pexels = st.text_input("Pexels API Key", value=ai_data.get("pexels_api_key", PEXELS_API_KEY), type="password")

            if st.button("💾 Save AI Engine Keys"):
                acct_mgr.save_ai_keys(groq_key=k_groq, gemini_key=k_gemini, pexels_key=k_pexels)
                st.success("AI Engine keys updated!")

    with tab_api:
        st.markdown("### ⚡ Programmatic Post API Sandbox")
        st.caption("Trigger autonomous video generation and publishing via HTTP POST requests from any app, script, Zapier, or Make.com.")

        st.markdown("#### 1. Live Endpoint Overview")
        st.markdown("""
        | Method | Endpoint | Description |
        | :--- | :--- | :--- |
        | `POST` | `/api/v1/generate` | Generate complete video, voiceover, thumbnails, and SEO |
        | `POST` | `/api/v1/publish` | Upload video to YouTube or Facebook |
        | `GET` | `/api/v1/trends` | Fetch real-time viral trends for any niche |
        | `GET` | `/api/v1/health` | Service health & connectivity ping |
        """)

        st.markdown("#### 2. Interactive POST API Tester")
        api_topic = st.text_input("Test Topic", value="Top 5 Artificial Intelligence Breakthroughs in 2026")
        c_a1, c_a2 = st.columns(2)
        with c_a1:
            api_niche = st.selectbox("API Niche", ["tech", "finance", "motivation", "mystery", "science"])
        with c_a2:
            api_format = st.selectbox("API Format", ["shorts", "tech_review", "motivational", "educational"])

        if st.button("🚀 Execute POST /api/v1/generate", type="primary", use_container_width=True):
            pipeline = ContentPipeline()
            with st.spinner("Processing API generation request..."):
                res = pipeline.run_full_pipeline(
                    topic=api_topic,
                    niche=api_niche,
                    content_type=api_format,
                    dry_run=True
                )
            st.success("HTTP 200 OK — Generation Complete!")
            st.json({
                "status": "success",
                "code": 200,
                "video_title": res.get("title"),
                "video_url": res.get("video_path"),
                "thumbnail_url": res.get("thumbnail_path"),
                "audio_url": res.get("audio_path"),
                "elapsed_seconds": res.get("elapsed_seconds")
            })

        st.markdown("#### 3. Integration Code Snippets")
        code_tab1, code_tab2 = st.tabs(["cURL", "Python Request"])
        with code_tab1:
            st.code("""
curl -X POST http://localhost:8000/api/v1/generate \\
  -H "Content-Type: application/json" \\
  -d '{
    "topic": "5 AI Inventions That Shocked Everyone in 2026",
    "niche": "tech",
    "content_type": "shorts",
    "orientation": "vertical",
    "auto_publish": false
  }'
            """, language="bash")
        with code_tab2:
            st.code("""
import requests

payload = {
    "topic": "5 AI Inventions That Shocked Everyone in 2026",
    "niche": "tech",
    "content_type": "shorts",
    "orientation": "vertical",
    "auto_publish": False
}

response = requests.post("http://localhost:8000/api/v1/generate", json=payload)
data = response.json()
print("Generated Video:", data["result"]["video_path"])
            """, language="python")


# ==============================================================================
# TAB 9: SOCIAL PUBLISHER
# ==============================================================================
elif menu == "📤 Social Publisher":
    render_dashboard_header(
        title="📤 Social Media Distribution",
        subtitle="Automate one-click publishing to YouTube Data API and Facebook Graph API."
    )

    latest = st.session_state.get("latest_production_result")
    if not isinstance(latest, dict):
        latest = {}
        
    def_video = latest.get("video_path", str(OUTPUT_DIR / "final_video.mp4")) if latest else str(OUTPUT_DIR / "final_video.mp4")
    def_title = latest.get("title", "Top 5 AI Innovations in 2026") if latest else "Top 5 AI Innovations in 2026"
    def_desc = latest.get("seo", {}).get("description", "Discover the latest AI tools changing the industry.") if (latest and isinstance(latest.get("seo"), dict)) else "Discover the latest AI tools changing the industry."

    v_file = st.text_input("Path to MP4 Video", value=def_video)
    p_title = st.text_input("Post Title", value=def_title)
    p_desc = st.text_area("Post Description", value=def_desc)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("▶️ Publish to YouTube (Simulation / Live)", type="primary", use_container_width=True):
            yt = YouTubeUploader()
            res = yt.upload_video(video_path=v_file, title=p_title, description=p_desc, dry_run=True)
            st.json(res)
    with c2:
        if st.button("📘 Publish to Facebook (Simulation / Live)", use_container_width=True):
            fb = FacebookPublisher()
            res = fb.publish_video(video_path=v_file, title=p_title, description=p_desc, dry_run=True)
            st.json(res)


# ==============================================================================
# TAB 10: MEDIA LIBRARY & DIAGNOSTICS
# ==============================================================================
elif menu == "🗄️ Media Library & Diagnostics":
    render_dashboard_header(
        title="🗄️ Media Library & System Diagnostics",
        subtitle="Asset library of rendered media packages and real-time engine health checks."
    )

    tab_lib, tab_diag = st.tabs(["📁 Production Asset Library", "🩺 Engine & API Health Diagnostics"])

    with tab_lib:
        history_file = OUTPUT_DIR / "pipeline_history.json"
        records = load_json(history_file, default=[])

        if not records:
            st.info("No videos generated yet. Head over to the One-Click Studio to create your first production!")
        else:
            st.markdown(f"##### 🎬 Total Productions: **{len(records)}**")
            for item in reversed(records):
                with st.expander(f"🎬 {item.get('title', 'Untitled')} — {item.get('timestamp', 'Recent')}", expanded=False):
                    c_m1, c_m2 = st.columns([1, 1])
                    with c_m1:
                        if item.get("video_path") and os.path.exists(item.get("video_path")):
                            st.video(item.get("video_path"))
                    with c_m2:
                        if item.get("thumbnail_path") and os.path.exists(item.get("thumbnail_path")):
                            st.image(item.get("thumbnail_path"), use_container_width=True)
                        st.json(item)

    with tab_diag:
        st.markdown("##### ⚡ Live Latency & Connectivity Monitor")
        if st.button("🩺 Run Full System Diagnostics", type="primary", use_container_width=True):
            with st.spinner("Pinging AI endpoints and testing synthesis pipelines..."):
                diag_data = run_system_diagnostics()
                st.session_state["diagnostics_results"] = diag_data

        diag_res = st.session_state.get("diagnostics_results", {})
        if diag_res:
            for engine_name, info in diag_res.items():
                st.markdown(f"""
                <div class="saas-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-weight: 700; color: #F8FAFC; font-size: 1.05rem;">{engine_name}</div>
                            <div style="font-size: 0.82rem; color: #94A3B8; margin-top: 2px;">{info['status']}</div>
                        </div>
                        <div style="text-align: right;">
                            <span class="kpi-badge badge-{'success' if info['connected'] else 'warning'}">{info['badge']}</span>
                            {f'<div style="font-size: 0.78rem; color: #10B981; margin-top: 4px; font-weight: 600;">⚡ {info["latency_ms"]} ms</div>' if info.get("latency_ms") else ''}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
