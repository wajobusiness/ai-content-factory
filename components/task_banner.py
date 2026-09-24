"""
Active Background Task Banner & Controller for AI Content Factory SaaS.
Displays live task progress across all pages with real-time Stop/Cancel controls.
"""

import time
import streamlit as st
from utils.task_runner import task_manager


def render_active_task_banner():
    """Renders persistent task banner at the top of the page if a task is active or recently finished."""
    active_task = task_manager.get_active_task()
    if not active_task:
        return

    summary = active_task.get_summary()
    status = summary["status"]

    if status == "running":
        progress_pct = int(summary["progress"] * 100)
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, rgba(99, 102, 241, 0.15) 0%, rgba(236, 72, 153, 0.15) 100%); border: 1px solid rgba(99, 102, 241, 0.4); border-radius: 12px; padding: 14px 18px; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #10B981; box-shadow: 0 0 10px #10B981; animation: pulse 1.5s infinite;"></span>
                    <strong style="color: #F8FAFC; font-size: 1rem;">Background Task Running: {summary['name']}</strong>
                </div>
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="color: #A5B4FC; font-size: 0.85rem; font-weight: 600;">⏱️ {summary['elapsed_seconds']}s</span>
                    <span class="kpi-badge badge-pro">{progress_pct}%</span>
                </div>
            </div>
            <div style="color: #CBD5E1; font-size: 0.85rem; margin-bottom: 10px;">📍 <em>{summary['current_step']}</em></div>
        </div>
        """, unsafe_allow_html=True)
        
        st.progress(summary["progress"])
        
        c_stop, c_ref = st.columns([1, 4])
        with c_stop:
            if st.button("🛑 Stop / Cancel Task", key="btn_stop_bg_task", type="primary", use_container_width=True):
                task_manager.cancel_active_task()
                st.warning("Cancellation signal sent to background task.")
                st.rerun()
        with c_ref:
            if st.button("🔄 Refresh Task Progress", key="btn_refresh_bg_task"):
                st.rerun()

    elif status == "completed":
        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 12px; padding: 12px 18px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
            <div style="color: #10B981; font-weight: 700; font-size: 0.95rem;">
                ✅ Task '{summary['name']}' completed successfully in {summary['elapsed_seconds']}s!
            </div>
        </div>
        """, unsafe_allow_html=True)
        if summary.get("result"):
            st.session_state["latest_production_result"] = summary["result"]
            st.session_state["workspace_topic"] = summary["result"].get("title", "")
        if st.button("Dismiss Notification", key="btn_dismiss_task_done"):
            task_manager.clear_active_task()
            st.rerun()

    elif status == "cancelled":
        st.markdown(f"""
        <div style="background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.35); border-radius: 12px; padding: 12px 18px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
            <div style="color: #FBBF24; font-weight: 700; font-size: 0.95rem;">
                🛑 Task '{summary['name']}' was stopped by user after {summary['elapsed_seconds']}s.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Dismiss", key="btn_dismiss_task_cancel"):
            task_manager.clear_active_task()
            st.rerun()

    elif status == "failed":
        st.markdown(f"""
        <div style="background: rgba(239, 68, 68, 0.12); border: 1px solid rgba(239, 68, 68, 0.35); border-radius: 12px; padding: 12px 18px; margin-bottom: 20px;">
            <div style="color: #EF4444; font-weight: 700; font-size: 0.95rem;">
                ❌ Task '{summary['name']}' failed: {summary.get('error', 'Unknown error')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Dismiss", key="btn_dismiss_task_failed"):
            task_manager.clear_active_task()
            st.rerun()


def render_sidebar_task_indicator():
    """Renders a compact task badge in the sidebar if a background job is running."""
    active_task = task_manager.get_active_task()
    if active_task and active_task.status == "running":
        summary = active_task.get_summary()
        pct = int(summary["progress"] * 100)
        st.sidebar.markdown(f"""
        <div style="background: rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.4); border-radius: 8px; padding: 8px 10px; margin-top: 8px; margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.75rem; color: #A5B4FC; font-weight: 700;">⚡ RUNNING ({pct}%)</span>
                <span style="font-size: 0.72rem; color: #94A3B8;">{summary['elapsed_seconds']}s</span>
            </div>
            <div style="font-size: 0.78rem; color: #F8FAFC; font-weight: 600; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{summary['name']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.sidebar.button("🛑 Stop Task", key="sidebar_stop_task_btn", use_container_width=True):
            task_manager.cancel_active_task()
            st.rerun()
