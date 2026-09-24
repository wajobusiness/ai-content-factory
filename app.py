"""
AI Content Factory Pro - Enterprise SaaS Web Dashboard
Interactive UI for automated video generation, trend research, voiceover, thumbnails, and SEO.
"""

import os
import sys
import time
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
from platforms.youtube_uploader import YouTubeUploader
from platforms.facebook_publisher import FacebookPublisher
from auto_scheduler import ContentPipeline
from utils.helpers import load_json

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

# Sidebar Navigation & Branding
st.sidebar.markdown("""
<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
    <div style="background: linear-gradient(135deg, #6366F1, #EC4899); width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; font-weight: 800; color: white;">⚡</div>
    <div>
        <div style="font-size: 1.15rem; font-weight: 800; color: #F8FAFC; letter-spacing: -0.02em;">ContentForge AI</div>
        <div style="font-size: 0.75rem; color: #94A3B8;">Autonomous Production Studio</div>
    </div>
</div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio(
    "Navigation",
    [
        "🚀 One-Click Studio",
        "🔍 Trend Radar",
        "📝 AI Script Studio",
        "🎙️ Voiceover Studio",
        "🎨 Visuals & A/B Thumbnails",
        "🎭 Cartoon Studio",
        "📈 SEO Engine",
        "📤 Social Publisher",
        "🗄️ Media Library & Diagnostics"
    ],
    index=0
)

# Render active workspace chip in sidebar if present
active_topic = get_workspace_topic()
if active_topic:
    st.sidebar.markdown(f"""
    <div style="background: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.25); border-radius: 8px; padding: 10px; margin-top: 10px;">
        <div style="font-size: 0.72rem; color: #A5B4FC; text-transform: uppercase; font-weight: 700;">Active Project Context</div>
        <div style="font-size: 0.82rem; color: #F8FAFC; font-weight: 600; margin-top: 3px; word-break: break-word;">{active_topic[:45]}...</div>
    </div>
    """, unsafe_allow_html=True)

render_api_status_sidebar()

# ==============================================================================
# TAB 1: ONE-CLICK PRODUCTION STUDIO
# ==============================================================================
if menu == "🚀 One-Click Studio":
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
        pipeline_steps = ["1. Trend & Script", "2. Voice & Subtitles", "3. Visuals & Motion", "4. Video Render", "5. SEO & Package"]
        stepper_placeholder = st.empty()
        status_placeholder = st.empty()

        stepper_placeholder.markdown('<div class="saas-card">Initializing Autonomous Engine...</div>', unsafe_allow_html=True)

        pipeline = ContentPipeline()
        with st.status("🎬 Running Autonomous Production Engine...", expanded=True) as status:
            render_stepper(pipeline_steps, 0)
            st.write("🔍 Identifying viral angles & crafting high-retention script...")
            
            res = pipeline.run_full_pipeline(
                topic=topic_input.strip() if topic_input.strip() else None,
                niche=niche_option,
                content_type=content_type,
                voice=selected_voice,
                orientation=orientation,
                resolution=resolution,
                enable_upload=enable_upload,
                dry_run=True
            )
            
            render_stepper(pipeline_steps, 4)
            status.update(label="✅ Complete Production Package Generated Successfully!", state="complete")

        st.session_state["latest_production_result"] = res
        st.session_state["workspace_topic"] = res.get("title", topic_input)
        st.success(f"🎉 Created '{res.get('title')}' in {res.get('elapsed_seconds')}s!")

    # Display Latest Production Results
    latest = st.session_state.get("latest_production_result")
    if latest:
        st.markdown("---")
        st.markdown("### 📦 Production Deliverables & Assets")

        # 1-Click ZIP Bundle Exporter
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
                st.success(f"Selected: '{t.get('title')}'! Head to One-Click Studio or Script Studio.")


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
elif menu == "🎭 Cartoon Studio":
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
elif menu == "📈 SEO Engine":
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
# TAB 8: SOCIAL PUBLISHER
# ==============================================================================
elif menu == "📤 Social Publisher":
    render_dashboard_header(
        title="📤 Social Media Distribution",
        subtitle="Automate one-click publishing to YouTube Data API and Facebook Graph API."
    )

    latest = st.session_state.get("latest_production_result", {})
    def_video = latest.get("video_path", str(OUTPUT_DIR / "final_video.mp4"))
    def_title = latest.get("title", "Top 5 AI Innovations in 2026")
    def_desc = latest.get("seo", {}).get("description", "Discover the latest AI tools changing the industry.")

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
# TAB 9: MEDIA LIBRARY & DIAGNOSTICS
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
