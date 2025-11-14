# ui_components.py — Reusable UI Components

import streamlit as st
from src.config.constants import __version__, AUTHOR, INTENT_COLORS


def badge(text: str, color: str) -> str:
    """Create a colored badge HTML."""
    return f'<span class="badge" style="background:{color}">{text}</span>'


def hero_banner():
    """Display application hero banner."""
    st.markdown(
        f"""<div style="text-align:center;padding:18px 8px;border-top:1px solid #e6e6e6;">
        <h2 style="margin:6px 0 10px 0;">🤖 LLM Search Intent Analyzer v{__version__}</h2>
        <p style="margin:6px 0 6px 0;">Built by <strong>{AUTHOR}</strong></p>
        <p style="margin:0;">Powered by <strong>Local LLM (Ollama)</strong> • No API Keys Required</p>
        </div>""",
        unsafe_allow_html=True,
    )


def app_footer():
    """Display application footer."""
    import datetime as dt

    st.markdown(
        f"""<hr style="margin-top:36px;"/>
        <div style="text-align:center;font-size:13px;color:#666;padding-bottom:12px;">
        <div><strong>LLM Search Intent Analyzer</strong> • v{__version__}</div>
        <div>© {dt.datetime.now().year} {AUTHOR} — MIT License</div>
        </div>""",
        unsafe_allow_html=True,
    )


def score_bars_html(scores: dict) -> str:
    """Create HTML for score bars visualization."""
    html = '<div style="margin-top:12px;">'
    for intent, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        color = INTENT_COLORS.get(intent, "#6b7280")
        html += f"""
        <div class="score-bar">
            <div class="score-label">{intent}</div>
            <div class="score-progress">
                <div class="score-fill" style="width:{score}%;background:{color}"></div>
            </div>
            <div class="score-value">{score:.1f}%</div>
        </div>
        """
    html += "</div>"
    return html


def render_query_card(row, badge_html: str, scores: dict):
    """Render a single query result card."""
    st.markdown(
        f"""<div class="card">
        <h4>{row["keyword"]} {badge_html}</h4>
        <div class="kv">
            <b>Secondary:</b> {row["secondary_intent"]} • 
            <b>Confidence:</b> {row["confidence_pct"]:.1f}%
        </div>
        <div class="reasoning">💭 <strong>Reasoning:</strong> {row["reasoning"]}</div>
        </div>""",
        unsafe_allow_html=True,
    )

    with st.expander("📊 View Detailed Scores"):
        st.markdown(score_bars_html(scores), unsafe_allow_html=True)
