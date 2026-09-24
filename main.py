"""
AI Content Factory - Command Line Interface (CLI)
Complete terminal control for automated video generation, research, voiceover, and scheduling.
"""

import sys
import argparse
import subprocess
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

ROOT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(ROOT_DIR))

from config import DEFAULT_VOICE, DEFAULT_ORIENTATION, DEFAULT_RESOLUTION
from research.trend_finder import TrendFinder
from content.script_generator import ScriptGenerator
from content.voiceover_gen import VoiceoverGenerator
from content.thumbnail_maker import ThumbnailMaker
from content.cartoon_studio import CartoonStudio
from seo.seo_engine import SEOEngine
from auto_scheduler import ContentPipeline, start_scheduler

console = Console()


def print_banner():
    console.print(Panel.fit(
        "[bold cyan]AI CONTENT FACTORY[/bold cyan] 🎬 [bold green]v2.0[/bold green]\n"
        "[dim]100% Free Autonomous AI Video Production & Social Publishing Engine[/dim]\n"
        "[dim]Powered by Groq • Gemini • Edge-TTS • Pollinations • Pexels[/dim]",
        border_style="bright_magenta"
    ))


def cmd_generate(args):
    print_banner()
    pipeline = ContentPipeline()
    console.print(f"[bold yellow]🚀 Launching Full Pipeline...[/bold yellow]")
    console.print(f"Topic: [bold white]{args.topic or 'Auto-Detect Trend'}[/bold white]")
    console.print(f"Niche: [bold white]{args.niche}[/bold white] | Style: [bold white]{args.type}[/bold white]")
    console.print(f"Orientation: [bold white]{args.orientation}[/bold white] | Voice: [bold white]{args.voice}[/bold white]\n")

    res = pipeline.run_full_pipeline(
        topic=args.topic,
        niche=args.niche,
        content_type=args.type,
        voice=args.voice,
        orientation=args.orientation,
        resolution=args.resolution,
        enable_upload=args.upload,
        dry_run=True
    )

    console.print(Panel(
        f"[bold green]✨ SUCCESS! Content Generated in {res.get('elapsed_seconds')}s[/bold green]\n\n"
        f"🎬 [bold]Video Path:[/bold] {res.get('video_path')}\n"
        f"🖼️ [bold]Thumbnail:[/bold] {res.get('thumbnail_path')}\n"
        f"🎙️ [bold]Audio:[/bold] {res.get('audio_path')}\n"
        f"📝 [bold]Title:[/bold] {res.get('title')}\n"
        f"🏷️ [bold]Tags:[/bold] {', '.join(res.get('seo', {}).get('tags', [])[:6])}...",
        title="Production Summary",
        border_style="green"
    ))


def cmd_trends(args):
    print_banner()
    finder = TrendFinder()
    console.print(f"[bold cyan]🔍 Scanning viral signals for niche: '{args.niche}'...[/bold cyan]\n")
    trends = finder.discover_all(niche=args.niche)

    table = Table(title=f"Viral Trends ({args.niche.upper()})", border_style="cyan")
    table.add_column("Rank", justify="center", style="bold yellow")
    table.add_column("Topic Title", style="bold white")
    table.add_column("Source", style="dim")
    table.add_column("Score", justify="center", style="bold green")

    for i, t in enumerate(trends[:10]):
        table.add_row(str(i + 1), t.get("title", "")[:60], t.get("source", ""), f"{t.get('viral_score', 0)}/100")

    console.print(table)


def cmd_script(args):
    print_banner()
    generator = ScriptGenerator()
    console.print(f"[bold cyan]📝 Writing script for: '{args.topic}'...[/bold cyan]\n")
    script = generator.generate_script(topic=args.topic, content_type=args.type, target_duration=args.duration)

    console.print(Panel(f"[bold yellow]Hook:[/bold yellow] {script.get('hook')}", title=script.get("title", "Script"), border_style="yellow"))
    for sc in script.get("scenes", []):
        console.print(f"[bold cyan]Scene {sc.get('scene_number')}:[/bold cyan] {sc.get('narration')}")
        console.print(f"  [dim]Visual: {sc.get('visual_prompt')}[/dim]\n")


def cmd_voice(args):
    print_banner()
    vg = VoiceoverGenerator()
    console.print(f"[bold cyan]🎙️ Synthesizing voiceover with voice '{args.voice}'...[/bold cyan]")
    res = vg.generate(text=args.text, voice=args.voice, output_name="cli_voiceover")
    console.print(f"[bold green]✅ Audio saved to:[/bold green] {res.get('audio_path')} (Duration: {res.get('duration')}s)")


def cmd_thumbnail(args):
    print_banner()
    tm = ThumbnailMaker()
    console.print(f"[bold cyan]🎨 Designing thumbnail for: '{args.title}'...[/bold cyan]")
    path = tm.create_thumbnail(title=args.title, badge_text=args.badge, ai_prompt=args.prompt)
    console.print(f"[bold green]✅ Thumbnail saved to:[/bold green] {path}")


def cmd_cartoon(args):
    print_banner()
    cs = CartoonStudio()
    console.print(f"[bold cyan]🎭 Creating cartoon episode for '{args.name}'...[/bold cyan]")
    ep = cs.create_cartoon_episode(premise=args.premise, character_name=args.name)
    console.print(f"[bold green]✅ Cartoon episode created![/bold green] Total scenes: {len(ep.get('scenes', []))}")


def cmd_seo(args):
    print_banner()
    engine = SEOEngine()
    console.print(f"[bold cyan]📈 Optimizing SEO for: '{args.topic}'...[/bold cyan]")
    seo = engine.optimize_video_seo(topic=args.topic, target_niche=args.niche)
    console.print(f"[bold yellow]Best Title:[/bold yellow] {seo.get('best_title')}")
    console.print(f"[bold yellow]Tags:[/bold yellow] {', '.join(seo.get('tags', []))}")


def cmd_schedule(args):
    print_banner()
    console.print(f"[bold green]⏰ Starting autonomous scheduler every {args.interval} hours...[/bold green]")
    start_scheduler(interval_hours=args.interval, niche=args.niche)


def cmd_dashboard(args):
    print_banner()
    console.print("[bold green]🚀 Launching Streamlit Web Dashboard...[/bold green]")
    app_path = ROOT_DIR / "app.py"
    subprocess.run(["streamlit", "run", str(app_path)])


def main():
    parser = argparse.ArgumentParser(description="AI Content Factory - Automated Video Creation & Publishing")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    p_gen = subparsers.add_parser("generate", help="Run full automated pipeline")
    p_gen.add_argument("--topic", type=str, default=None, help="Video topic")
    p_gen.add_argument("--niche", type=str, default="tech", help="Content niche")
    p_gen.add_argument("--type", type=str, default="tech_review", help="Content type")
    p_gen.add_argument("--voice", type=str, default=DEFAULT_VOICE, help="Voice identifier")
    p_gen.add_argument("--orientation", type=str, default=DEFAULT_ORIENTATION, help="Orientation")
    p_gen.add_argument("--resolution", type=str, default=DEFAULT_RESOLUTION, help="Resolution")
    p_gen.add_argument("--upload", action="store_true", help="Enable social upload")

    p_tr = subparsers.add_parser("trends", help="Discover trending topics")
    p_tr.add_argument("--niche", type=str, default="tech", help="Niche filter")

    p_sc = subparsers.add_parser("script", help="Generate video script")
    p_sc.add_argument("--topic", type=str, required=True, help="Script topic")
    p_sc.add_argument("--type", type=str, default="tech_review", help="Content style")
    p_sc.add_argument("--duration", type=str, default="60s", help="Target length")

    p_vc = subparsers.add_parser("voice", help="Generate AI voiceover")
    p_vc.add_argument("--text", type=str, required=True, help="Text to speak")
    p_vc.add_argument("--voice", type=str, default=DEFAULT_VOICE, help="Voice name")

    p_th = subparsers.add_parser("thumbnail", help="Design thumbnail")
    p_th.add_argument("--title", type=str, required=True, help="Thumbnail headline text")
    p_th.add_argument("--badge", type=str, default="NEW 2026", help="Badge text")
    p_th.add_argument("--prompt", type=str, default=None, help="Background image AI prompt")

    p_ct = subparsers.add_parser("cartoon", help="Create cartoon series episode")
    p_ct.add_argument("--premise", type=str, required=True, help="Story premise")
    p_ct.add_argument("--name", type=str, default="Pip the Dragon", help="Character name")

    p_seo = subparsers.add_parser("seo", help="Generate SEO package")
    p_seo.add_argument("--topic", type=str, required=True, help="Topic for SEO")
    p_seo.add_argument("--niche", type=str, default="technology", help="Niche")

    p_sch = subparsers.add_parser("schedule", help="Start background auto-poster")
    p_sch.add_argument("--interval", type=int, default=24, help="Interval in hours")
    p_sch.add_argument("--niche", type=str, default="tech", help="Niche to auto-post")

    subparsers.add_parser("dashboard", help="Launch Streamlit dashboard")

    args = parser.parse_args()

    if not args.command:
        print_banner()
        console.print("[bold yellow]Interactive Quick Menu:[/bold yellow]")
        console.print("1. 🚀 Run One-Click Video Generator")
        console.print("2. 🔍 Scan Viral Trends")
        console.print("3. 📝 Write AI Script")
        console.print("4. 🎙️ Generate Voiceover")
        console.print("5. 🎨 Create High-CTR Thumbnail")
        console.print("6. 🖥️ Launch Streamlit Web Dashboard")
        console.print("7. ⏰ Start Auto Scheduler")
        
        choice = Prompt.ask("\nChoose an option (1-7)", choices=["1", "2", "3", "4", "5", "6", "7"], default="1")
        if choice == "1":
            topic = Prompt.ask("Enter Topic (or press enter for trend auto-detect)", default="")
            args.topic = topic if topic else None
            args.niche = Prompt.ask("Enter Niche", default="tech")
            args.type = "tech_review"
            args.voice = DEFAULT_VOICE
            args.orientation = DEFAULT_ORIENTATION
            args.resolution = DEFAULT_RESOLUTION
            args.upload = False
            cmd_generate(args)
        elif choice == "2":
            args.niche = Prompt.ask("Enter Niche", default="tech")
            cmd_trends(args)
        elif choice == "3":
            args.topic = Prompt.ask("Enter Topic", default="The Future of AI in 2026")
            args.type = "tech_review"
            args.duration = "60s"
            cmd_script(args)
        elif choice == "4":
            args.text = Prompt.ask("Enter Narration Text", default="Hello and welcome back to our channel!")
            args.voice = DEFAULT_VOICE
            cmd_voice(args)
        elif choice == "5":
            args.title = Prompt.ask("Thumbnail Title", default="AI WILL CHANGE EVERYTHING")
            args.badge = "2026 UPDATE"
            args.prompt = "futuristic technology hologram"
            cmd_thumbnail(args)
        elif choice == "6":
            cmd_dashboard(args)
        elif choice == "7":
            args.interval = 24
            args.niche = "tech"
            cmd_schedule(args)
        return

    handlers = {
        "generate": cmd_generate,
        "trends": cmd_trends,
        "script": cmd_script,
        "voice": cmd_voice,
        "thumbnail": cmd_thumbnail,
        "cartoon": cmd_cartoon,
        "seo": cmd_seo,
        "schedule": cmd_schedule,
        "dashboard": cmd_dashboard
    }

    handler = handlers.get(args.command)
    if handler:
        handler(args)


if __name__ == "__main__":
    main()

