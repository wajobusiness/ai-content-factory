"""
Theme and Design System for AI Content Factory SaaS.
Injects custom glassmorphism styles, glowing accents, modern typography, and responsive cards.
"""

import streamlit as st


def inject_custom_theme():
    """Injects high-end dark SaaS CSS styling with glassmorphism and animations."""
    st.markdown("""
    <style>
        /* Base typography & variables */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

        :root {
            --primary-gradient: linear-gradient(135deg, #6366F1 0%, #A855F7 50%, #EC4899 100%);
            --accent-gradient: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
            --surface-bg: rgba(18, 22, 34, 0.75);
            --surface-card: rgba(255, 255, 255, 0.035);
            --border-glow: rgba(99, 102, 241, 0.25);
            --border-subtle: rgba(255, 255, 255, 0.08);
            --text-main: #F8FAFC;
            --text-muted: #94A3B8;
            --badge-green: rgba(16, 185, 129, 0.15);
            --badge-green-text: #10B981;
            --badge-purple: rgba(168, 85, 247, 0.15);
            --badge-purple-text: #C084FC;
            --badge-amber: rgba(245, 158, 11, 0.15);
            --badge-amber-text: #FBBF24;
        }

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }

        code, pre, .stCode {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* Glassmorphic Container Cards */
        .saas-card {
            background: var(--surface-card);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--border-subtle);
            border-radius: 14px;
            padding: 20px;
            margin-bottom: 16px;
            transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
            position: relative;
            overflow: hidden;
        }

        .saas-card:hover {
            border-color: rgba(99, 102, 241, 0.4);
            transform: translateY(-2px);
            box-shadow: 0 12px 30px -10px rgba(99, 102, 241, 0.18);
        }

        .saas-card.highlight {
            border-color: rgba(168, 85, 247, 0.4);
            background: linear-gradient(180deg, rgba(168, 85, 247, 0.06) 0%, rgba(18, 22, 34, 0.6) 100%);
        }

        /* Hero Banner Headers */
        .saas-hero-header {
            font-size: 2.35rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.25rem;
            line-height: 1.2;
        }

        .saas-hero-sub {
            font-size: 1.05rem;
            font-weight: 400;
            color: var(--text-muted);
            margin-bottom: 1.5rem;
            line-height: 1.5;
        }

        /* Metric & KPI Badges */
        .kpi-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border-subtle);
            border-radius: 12px;
            padding: 14px 18px;
            margin-bottom: 12px;
        }

        .kpi-title {
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            font-weight: 600;
        }

        .kpi-value {
            font-size: 1.45rem;
            font-weight: 700;
            color: var(--text-main);
            margin-top: 2px;
        }

        .kpi-badge {
            font-size: 0.75rem;
            font-weight: 600;
            padding: 3px 8px;
            border-radius: 9999px;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }

        .badge-success {
            background: var(--badge-green);
            color: var(--badge-green-text);
            border: 1px solid rgba(16, 185, 129, 0.3);
        }

        .badge-pro {
            background: var(--badge-purple);
            color: var(--badge-purple-text);
            border: 1px solid rgba(168, 85, 247, 0.3);
        }

        .badge-warning {
            background: var(--badge-amber);
            color: var(--badge-amber-text);
            border: 1px solid rgba(245, 158, 11, 0.3);
        }

        /* Preset Chips */
        .preset-badge {
            display: inline-block;
            background: rgba(99, 102, 241, 0.12);
            border: 1px solid rgba(99, 102, 241, 0.25);
            color: #C7D2FE;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.78rem;
            font-weight: 600;
            margin-right: 6px;
            margin-bottom: 6px;
        }

        /* Launchpad Grid Card */
        .launchpad-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border-subtle);
            border-radius: 14px;
            padding: 20px;
            height: 100%;
            transition: all 0.25s ease;
            position: relative;
        }

        .launchpad-card:hover {
            background: rgba(99, 102, 241, 0.07);
            border-color: rgba(99, 102, 241, 0.4);
            transform: translateY(-3px);
            box-shadow: 0 10px 25px -8px rgba(99, 102, 241, 0.2);
        }

        .launchpad-icon {
            width: 44px;
            height: 44px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.4rem;
            margin-bottom: 12px;
        }

        .sidebar-section-header {
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #64748B;
            font-weight: 700;
            margin-top: 14px;
            margin-bottom: 6px;
        }

        /* Custom Streamlit Tabs & Buttons polish */
        .stButton>button {
            border-radius: 10px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
        }

        .stButton>button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
        }

        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 7px;
            height: 7px;
        }
        ::-webkit-scrollbar-track {
            background: rgba(15, 23, 42, 0.6);
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.15);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(99, 102, 241, 0.5);
        }
    </style>
    """, unsafe_allow_html=True)
