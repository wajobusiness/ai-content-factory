"""
Pipeline Progress Stepper Component for AI Content Factory SaaS.
"""

from typing import List
import streamlit as st


def render_stepper(steps: List[str], current_index: int):
    """Renders a modern glowing step progress bar."""
    step_html = ""
    for idx, step in enumerate(steps):
        is_active = idx == current_index
        is_done = idx < current_index
        
        status_class = "done" if is_done else ("active" if is_active else "pending")
        dot_color = "#10B981" if is_done else ("#6366F1" if is_active else "#475569")
        text_color = "#F8FAFC" if (is_done or is_active) else "#64748B"
        icon = "✓" if is_done else f"{idx + 1}"
        
        step_html += f"""
        <div style="flex: 1; text-align: center; position: relative;">
            <div style="width: 28px; height: 28px; border-radius: 50%; background: {dot_color}; color: #FFFFFF; font-size: 0.8rem; font-weight: 700; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 4px; box-shadow: {('0 0 12px rgba(99, 102, 241, 0.6)' if is_active else 'none')};">
                {icon}
            </div>
            <div style="font-size: 0.75rem; font-weight: 600; color: {text_color};">{step}</div>
        </div>
        """

    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 12px; padding: 14px 10px; margin-bottom: 20px;">
        {step_html}
    </div>
    """, unsafe_allow_html=True)
