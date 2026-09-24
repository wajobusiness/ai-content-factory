"""
AI Content Factory - Streamlit Web Dashboard
Interactive UI for automated video generation, trend research, voiceover, thumbnails, and SEO.
"""

import os
import sys
from pathlib import Path
import streamlit as st

# Add current folder to sys.path
ROOT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(ROOT_DIR))

from config import (
    AVAILABLE_VOICES,
    DEFAULT_VOICE,
    OUTPUT_DIR,
    GROQ_API_KEY,
    GEMINI_API_KEY,
    PEXELS_API_KEY
)
from research.trend_finder import TrendFinder
from content.script_generator import ScriptGenerator
from content.voiceover_gen import VoiceoverGenerator
from content.ai_image_gen import AIImageGenerator
from content.ai_story_gen import AIStoryGenerator
from content.thumbnail_maker import ThumbnailMaker
from content.cartoon_studio import CartoonStudio
from seo.seo_engine import SEOEngine
from platforms.youtube_uploader import YouTubeUploader
from platforms.facebook_publisher import FacebookPublisher
from auto_scheduler import ContentPipeline
from utils.helpers import load_json

st.set_page_config(
    page_title="AI Content Factory",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #FF4B4B, #FF8533, #FFCC00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #888888;
        margin-bottom: 1.5rem;
    }
    .card {
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("### 🎬 AI Content Factory")
st.sidebar.caption("100% Free AI Video & Media Engine")

menu = st.sidebar.radio(
    "Navigation",
    [
        "🚀 One-Click Generator",
        "🔍 Trend Radar",
        "📝 AI Script Studio",
        "🎙️ Voiceover Studio",
        "🎨 AI Visuals & Thumbnails",
        "🎭 Cartoon Studio",
        "📈 SEO Engine",
        "📤 Social Publisher",
        "📜 Pipeline History"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("#### 🔑 API Status")
st.sidebar.markdown(f"• **Groq LLM**: {'🟢 Connected' if GROQ_API_KEY else '⚪ Fallback Ready'}")
st.sidebar.markdown(f"• **Gemini LLM**: {'🟢 Connected' if GEMINI_API_KEY else '⚪ Fallback Ready'}")
st.sidebar.markdown(f"• **Edge-TTS**: 🟢 100% Free (Unlimited)")
st.sidebar.markdown(f"• **Pollinations AI**: 🟢 100% Free (Unlimited)")
st.sidebar.markdown(f"• **Pexels Stock**: {'🟢 Connected' if PEXELS_API_KEY else '⚪ AI Fallback'}")

# TAB 1: ONE-CLICK GENERATOR
if menu == "🚀 One-Click Generator":
    st.markdown('<div class="main-header">🚀 One-Click AI Content Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Generate complete YouTube & TikTok videos with AI script, voiceover, visuals, thumbnail & SEO in seconds.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### ⚙️ Configuration")
        niche_option = st.selectbox("Select Niche", ["tech", "finance", "motivation", "mystery", "cartoons", "science", "general"])
        topic_input = st.text_input("Custom Topic (or leave blank to auto-detect trend)", placeholder="e.g. Top 5 AI Tools That Will Replace Entire Teams in 2026")
        
        c1, c2 = st.columns(2)
        with c1:
            content_type = st.selectbox("Content Style", ["tech_review", "motivational", "news_update", "cartoon_series", "educational", "mystery", "shorts"])
            orientation = st.selectbox("Orientation", ["landscape", "vertical", "square"])
        with c2:
            voice_choice = st.selectbox("Voice", list(AVAILABLE_VOICES.keys()))
            selected_voice = AVAILABLE_VOICES[voice_choice]
            resolution = st.selectbox("Resolution", ["1080p", "720p"])

        enable_upload = st.checkbox("Simulate Social Upload (YouTube & Facebook)", value=True)
        generate_btn = st.button("✨ Generate Full Content Package", type="primary", use_container_width=True)

    with col2:
        st.markdown("#### 📊 System Overview")
        m1, m2, m3 = st.columns(3)
        m1.metric("Pipeline Cost", "$0.00", "100% Free")
        m2.metric("Est. Time", "~30-60s", "Instant")
        m3.metric("Video Format", f"{orientation.capitalize()} {resolution}", "HD")

        st.info("💡 **How it works:**\n1. Auto-discovers viral trends & writes retention script\n2. Generates natural Microsoft Neural voiceover & SRT\n3. Creates cinematic visual scenes & ambient soundtrack\n4. Assembles pro video with Ken Burns motion & audio ducking\n5. Renders high-CTR thumbnail & SEO tags")

    if generate_btn:
        pipeline = ContentPipeline()
        with st.status("🎬 Running Full Production Pipeline...", expanded=True) as status:
            st.write("🔍 Discovering trend & crafting retention script...")
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
            status.update(label="✅ Content Package Created Successfully!", state="complete")

        st.success(f"🎉 Created '{res.get('title')}' in {res.get('elapsed_seconds')}s!")

        r_col1, r_col2 = st.columns([1, 1])

        with r_col1:
            st.markdown("### 🎬 Rendered Video")
            if res.get("video_path") and os.path.exists(res.get("video_path")):
                st.video(res.get("video_path"))
                with open(res.get("video_path"), "rb") as vf:
                    st.download_button("⬇️ Download Video (MP4)", vf, file_name=os.path.basename(res.get("video_path")), mime="video/mp4")

            st.markdown("### 🖼️ High-CTR Thumbnail")
            if res.get("thumbnail_path") and os.path.exists(res.get("thumbnail_path")):
                st.image(res.get("thumbnail_path"), use_column_width=True)
                with open(res.get("thumbnail_path"), "rb") as tf:
                    st.download_button("⬇️ Download Thumbnail", tf, file_name=os.path.basename(res.get("thumbnail_path")), mime="image/jpeg")

        with r_col2:
            st.markdown("### 🎙️ Audio & Subtitles")
            if res.get("audio_path") and os.path.exists(res.get("audio_path")):
                st.audio(res.get("audio_path"))
            if res.get("srt_path") and os.path.exists(res.get("srt_path")):
                with open(res.get("srt_path"), "r", encoding="utf-8") as sf:
                    st.download_button("⬇️ Download Subtitles (.SRT)", sf.read(), file_name=os.path.basename(res.get("srt_path")), mime="text/plain")

            st.markdown("### 📈 SEO Package")
            seo = res.get("seo", {})
            st.text_input("Best Title", value=seo.get("best_title", res.get("title", "")))
            st.text_area("Description", value=seo.get("description", ""), height=150)
            st.text_input("Tags", value=", ".join(seo.get("tags", [])))
            st.text_input("Hashtags", value=" ".join(seo.get("hashtags", [])))

# TAB 2: TREND RADAR
elif menu == "🔍 Trend Radar":
    st.markdown('<div class="main-header">🔍 Viral Trend Radar</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Real-time trending topics from Google Trends, Reddit, and Hacker News.</div>', unsafe_allow_html=True)

    niche_filter = st.selectbox("Filter Niche", ["tech", "finance", "motivation", "mystery", "cartoons", "science", "general"])
    
    if st.button("🔄 Scan Current Trends", type="primary"):
        finder = TrendFinder()
        with st.spinner("Scanning viral signals..."):
            trends = finder.discover_all(niche=niche_filter)
        
        st.write(f"Found **{len(trends)}** hot topics:")
        for t in trends:
            st.markdown(f"""
            <div class="card">
                <h4>🔥 {t.get('title')}</h4>
                <p style="color: #aaa; margin: 4px 0;"><strong>Source:</strong> {t.get('source')} | <strong>Viral Score:</strong> <span style="color:#00ff88;">{t.get('viral_score')}/100</span> | <strong>Category:</strong> {t.get('category')}</p>
            </div>
            """, unsafe_allow_html=True)

# TAB 3: AI SCRIPT STUDIO
elif menu == "📝 AI Script Studio":
    st.markdown('<div class="main-header">📝 AI Script & Story Studio</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Draft scene-by-scene high-retention video scripts.</div>', unsafe_allow_html=True)

    c1, c2 = st.columns([2, 1])
    with c1:
        s_topic = st.text_input("Video Topic", value="Why Quantum Computing Will Disrupt Cryptography in 2026")
    with c2:
        s_type = st.selectbox("Content Type", ["tech_review", "news_update", "motivational", "educational", "mystery", "shorts"])

    s_duration = st.select_slider("Target Duration", options=["30s", "60s", "2m", "5m"], value="60s")

    if st.button("✍️ Generate Script", type="primary"):
        script_gen = ScriptGenerator()
        with st.spinner("Writing structured multi-scene script..."):
            script_data = script_gen.generate_script(topic=s_topic, content_type=s_type, target_duration=s_duration)
        
        st.subheader(f"📌 {script_data.get('title', 'Video Script')}")
        st.info(f"**Hook:** {script_data.get('hook')}")

        for sc in script_data.get("scenes", []):
            with st.expander(f"Scene {sc.get('scene_number', 1)}: {sc.get('section', 'Scene')} ({sc.get('duration_seconds', 8)}s)", expanded=True):
                st.markdown(f"**🗣️ Narration:** {sc.get('narration')}")
                st.markdown(f"**🎨 Visual Prompt:** `{sc.get('visual_prompt')}`")
                st.markdown(f"**📺 On-Screen Text:** `{sc.get('on_screen_text')}`")

        st.text_area("Full Script", value=script_data.get("full_voiceover_text", ""), height=150)

# TAB 4: VOICEOVER STUDIO
elif menu == "🎙️ Voiceover Studio":
    st.markdown('<div class="main-header">🎙️ Neural Voiceover Studio</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">100% Free natural human voice synthesis powered by Edge-TTS.</div>', unsafe_allow_html=True)

    text_input = st.text_area(
        "Narration Text",
        value="Welcome back! In today's video, we are breaking down the biggest breakthrough in artificial intelligence. Don't forget to like and subscribe!",
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

    if st.button("🔊 Synthesize Voiceover", type="primary"):
        vg = VoiceoverGenerator()
        with st.spinner("Synthesizing audio & extracting subtitles..."):
            v_res = vg.generate(text=text_input, voice=chosen_voice, rate=speed_rate, pitch=pitch_val)
        
        st.success(f"Generated {v_res.get('duration')}s voiceover!")
        st.audio(v_res.get("audio_path"))
        
        if v_res.get("srt_path"):
            with open(v_res.get("srt_path"), "r", encoding="utf-8") as f:
                st.text_area("Generated SRT Subtitles", value=f.read(), height=150)

# TAB 5: AI VISUALS & THUMBNAILS
elif menu == "🎨 AI Visuals & Thumbnails":
    st.markdown('<div class="main-header">🎨 AI Visuals & Thumbnail Maker</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Generate stunning 8K AI artwork and high-CTR YouTube thumbnails.</div>', unsafe_allow_html=True)

    tab_vis, tab_thumb = st.tabs(["🖼️ AI Image Generator", "🏷️ High-CTR Thumbnail Designer"])

    with tab_vis:
        img_prompt = st.text_input("Visual Prompt", value="Futuristic robotic scientist creating glowing holographic interface, ultra detailed")
        c1, c2 = st.columns(2)
        with c1:
            style = st.selectbox("Art Style", ["cinematic", "3d_cartoon", "anime", "cyberpunk", "photorealistic", "digital_art"])
        with c2:
            dim_choice = st.selectbox("Aspect Ratio", ["Landscape 16:9 (1280x720)", "Vertical 9:16 (720x1280)", "Square 1:1 (1024x1024)"])

        if st.button("✨ Generate AI Image", type="primary"):
            im_gen = AIImageGenerator()
            w, h = (1280, 720) if "Landscape" in dim_choice else ((720, 1280) if "Vertical" in dim_choice else (1024, 1024))
            with st.spinner("Generating image via Pollinations AI..."):
                img_p = im_gen.generate_image(prompt=img_prompt, style=style, width=w, height=h)
            st.image(img_p, caption=f"Generated Image ({style})", use_column_width=True)

    with tab_thumb:
        t_title = st.text_input("Thumbnail Title Text", value="THIS CHANGES EVERYTHING!")
        t_badge = st.text_input("Badge Text", value="NEW 2026")
        t_color = st.selectbox("Text Color", ["yellow", "white", "red", "cyan", "neon_green", "orange"])
        t_bg_prompt = st.text_input("Background Image Prompt", value="glowing futuristic cyberspace matrix")

        if st.button("🎨 Create Thumbnail", type="primary"):
            tm = ThumbnailMaker()
            with st.spinner("Designing high-CTR thumbnail..."):
                thumb_out = tm.create_thumbnail(
                    title=t_title,
                    ai_prompt=t_bg_prompt,
                    badge_text=t_badge,
                    main_color=t_color
                )
            st.image(thumb_out, caption="High-CTR Thumbnail", use_column_width=True)

# TAB 6: CARTOON STUDIO
elif menu == "🎭 Cartoon Studio":
    st.markdown('<div class="main-header">🎭 Cartoon Studio</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Create animated character stories with comic speech bubbles and sound effects.</div>', unsafe_allow_html=True)

    c_premise = st.text_input("Story Premise", value="The tiny dragon who was scared of sparks learns to light up the dark forest")
    c1, c2 = st.columns(2)
    with c1:
        c_name = st.text_input("Character Name", value="Pip the Dragon")
    with c2:
        c_desc = st.text_input("Character Description", value="a cute baby purple dragon with big green eyes and glowing wings")

    if st.button("🎬 Create Cartoon Episode", type="primary"):
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
            st.image(sc.get("image_path"), caption=f"Scene {sc.get('scene_number')}: {sc.get('narration')}")

# TAB 7: SEO ENGINE
elif menu == "📈 SEO Engine":
    st.markdown('<div class="main-header">📈 SEO & Metadata Optimizer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Generate viral titles, keyword-dense descriptions, and tags.</div>', unsafe_allow_html=True)

    seo_topic = st.text_input("Topic for SEO Optimization", value="Top 5 Passive Income Ideas for Beginners in 2026")
    seo_niche = st.selectbox("Niche", ["technology", "finance", "motivation", "health", "gaming", "education"])

    if st.button("🚀 Optimize SEO", type="primary"):
        engine = SEOEngine()
        with st.spinner("Calculating viral hooks and SEO score..."):
            res = engine.optimize_video_seo(topic=seo_topic, target_niche=seo_niche)
        
        st.metric("Clickability Score", f"{res.get('clickability_score', 92)}/100", "High CTR")
        st.subheader("🎯 Primary Title")
        st.code(res.get("best_title"))

        st.subheader("💡 Alternative Title Hooks")
        for alt in res.get("alternative_titles", []):
            st.markdown(f"• {alt}")

        st.subheader("📝 SEO Description")
        st.text_area("Description Text", value=res.get("description"), height=180)

        st.subheader("🏷️ Tags")
        st.code(", ".join(res.get("tags", [])))

# TAB 8: SOCIAL PUBLISHER
elif menu == "📤 Social Publisher":
    st.markdown('<div class="main-header">📤 Social Media Publisher</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Automated posting to YouTube Data API and Facebook Graph API.</div>', unsafe_allow_html=True)

    v_file = st.text_input("Path to MP4 Video", value=str(OUTPUT_DIR / "final_video.mp4"))
    p_title = st.text_input("Post Title", value="Top 5 AI Innovations in 2026")
    p_desc = st.text_area("Post Description", value="Discover the latest AI tools changing the industry. Like and subscribe!")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("▶️ Upload to YouTube (Simulation / Live)", type="primary"):
            yt = YouTubeUploader()
            res = yt.upload_video(video_path=v_file, title=p_title, description=p_desc, dry_run=True)
            st.json(res)
    with c2:
        if st.button("📘 Publish to Facebook (Simulation / Live)"):
            fb = FacebookPublisher()
            res = fb.publish_video(video_path=v_file, title=p_title, description=p_desc, dry_run=True)
            st.json(res)

# TAB 9: PIPELINE HISTORY
elif menu == "📜 Pipeline History":
    st.markdown('<div class="main-header">📜 Production History</div>', unsafe_allow_html=True)
    history_file = OUTPUT_DIR / "pipeline_history.json"
    records = load_json(history_file, default=[])

    if not records:
        st.info("No videos generated yet. Head over to the One-Click Generator to create your first video!")
    else:
        st.write(f"Total videos generated: **{len(records)}**")
        for item in reversed(records):
            with st.expander(f"🎬 {item.get('title')} ({item.get('timestamp')})"):
                st.json(item)

