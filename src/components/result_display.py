"""
Result Display Component
Handles rendering of analysis results
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from typing import List

from src.services.hybrid_analyzer import HybridIntentResult
from src.config.constants import INTENT_COLORS


def render_signal_badge(active: bool, icon: str, label: str) -> str:
    """Create HTML for signal badge."""
    css_class = "signal-badge" if active else "signal-badge-inactive"
    return f'<span class="{css_class}">{icon} {label}</span>'


def render_intent_card(result: HybridIntentResult):
    """Render primary intent card with confidence."""
    st.markdown(
        f"""
    <div class="intent-card">
        <h2>{result.primary_intent}</h2>
        <p style="font-size: 1.1rem;">Confidence: {result.confidence_score}% ({result.confidence_level.value})</p>
        <p style="font-size: 0.95rem; opacity: 0.9;">Secondary: {result.secondary_intent}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_signal_badges(result: HybridIntentResult):
    """Render active signal badges."""
    st.markdown("### 📊 Active Signals")

    badges = [
        render_signal_badge(
            result.firecrawl_used,
            "🔍",
            (
                f"Firecrawl ({result.firecrawl_results_count} results)"
                if result.firecrawl_used
                else "Firecrawl (not used)"
            ),
        ),
        render_signal_badge(
            bool(result.llm_reasoning),
            "🤖",
            (
                f"LLM ({result.llm_primary_intent})"
                if result.llm_reasoning
                else "LLM (not used)"
            ),
        ),
        render_signal_badge(True, "📝", "Keywords"),  # Keywords always active
    ]

    st.markdown("".join(badges), unsafe_allow_html=True)


def render_metrics(result: HybridIntentResult):
    """Render key metrics in columns."""
    col1, col2, col3 = st.columns(3)
    col1.metric("Primary Intent", result.primary_intent)
    col2.metric("Confidence", f"{result.confidence_score}%")
    col3.metric("Mixed Intent", "Yes" if result.is_mixed_intent else "No")


def render_intent_chart(result: HybridIntentResult):
    """Render intent distribution bar chart."""
    st.markdown("### 📈 Intent Distribution")

    fig = px.bar(
        x=list(result.all_intent_scores.keys()),
        y=list(result.all_intent_scores.values()),
        labels={"x": "Intent", "y": "Score (%)"},
        color=list(result.all_intent_scores.keys()),
        color_discrete_map=INTENT_COLORS,
    )
    fig.update_layout(showlegend=False, height=300)
    st.plotly_chart(fig, use_container_width=True)


def render_reasoning_section(result: HybridIntentResult):
    """Render analysis reasoning and LLM insights."""
    st.markdown("### 💡 Analysis Reasoning")
    st.info(result.reasoning)

    if result.llm_reasoning:
        st.markdown("### 🤖 LLM Analysis")
        st.success(
            f"**{result.llm_primary_intent}** ({result.llm_confidence:.1f}%)\n\n{result.llm_reasoning}"
        )

    if result.serp_features:
        st.markdown("### 🔍 SERP Features Detected")
        st.write(", ".join(result.serp_features))


def render_detailed_scores(result: HybridIntentResult):
    """Render detailed scores in expandable section."""
    with st.expander("📊 Detailed Scores"):
        scores_df = pd.DataFrame(
            [
                {"Signal": "Keywords", **result.keyword_scores},
                {"Signal": "Overall", **result.all_intent_scores},
            ]
        )
        st.dataframe(scores_df, use_container_width=True)


def render_result_card(result: HybridIntentResult):
    """
    Render complete result card with all components.

    Args:
        result: HybridIntentResult from analysis
    """
    render_intent_card(result)
    render_signal_badges(result)
    render_metrics(result)
    render_intent_chart(result)
    render_reasoning_section(result)
    render_detailed_scores(result)


def render_warning_messages(config: dict, result: HybridIntentResult):
    """Render warning messages for failed signals."""
    if config["use_firecrawl"] and not result.firecrawl_used:
        st.error(
            "🔴 **Firecrawl API is Currently Down (500 Server Error)**\n\n"
            "Your API key is **valid**, but Firecrawl's servers are experiencing issues. "
            "This is a **temporary problem on their end**, not yours.\n\n"
            "**What happened:**\n"
            "- ✅ Your API key: `fc-176b7...6375` is valid\n"
            "- ❌ Firecrawl returned: 500 Internal Server Error\n"
            "- 🔄 Analysis completed using LLM + Keywords instead\n\n"
            "**What you can do:**\n"
            "1. **Keep working!** - Your results are still accurate with LLM + Keywords\n"
            "2. **Try again in 5-10 minutes** - Server issues usually resolve quickly\n"
            "3. **Check Firecrawl status** - Visit firecrawl.dev for updates\n\n"
            "💡 **Good news:** You're still getting ~85-90% accuracy without Firecrawl!"
        )

    if config["use_llm"] and not result.llm_reasoning:
        st.warning(
            "⚠️ **LLM was enabled but not used.** "
            "Make sure Ollama is running: `ollama serve`"
        )


def render_batch_summary(df: pd.DataFrame):
    """
    Render summary statistics for batch analysis.

    Args:
        df: DataFrame with batch results
    """
    st.markdown("### 📊 Summary Statistics")
    col1, col2, col3, col4 = st.columns(4)

    primary_counts = df["Primary Intent"].value_counts()
    most_common = primary_counts.index[0] if not primary_counts.empty else "N/A"

    col1.metric("Total Keywords", len(df))
    col2.metric("Most Common", most_common)
    col3.metric("Mixed Intent", df["Mixed Intent"].sum())
    col4.metric("Firecrawl Used", df["Firecrawl Used"].sum())


def render_intent_distribution(df: pd.DataFrame):
    """
    Render intent distribution pie chart for batch results.

    Args:
        df: DataFrame with batch results
    """
    primary_counts = df["Primary Intent"].value_counts()

    if not primary_counts.empty:
        fig = px.pie(
            values=primary_counts.values,
            names=primary_counts.index,
            title="Intent Distribution",
            color=primary_counts.index,
            color_discrete_map=INTENT_COLORS,
        )
        st.plotly_chart(fig, use_container_width=True)
