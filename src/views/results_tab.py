# results_tab.py — Results Tab View

import json
import datetime as dt
import streamlit as st
from src.config.constants import INTENTS, INTENT_COLORS
from src.components.ui_components import badge, render_query_card
from src.utils.data_processor import filter_dataframe


def render_results_tab(df):
    """Render the results tab with filters and cards."""
    if df is None or df.empty:
        st.info("👈 Run an analysis in the Input tab to see results here.")
        return

    # Filters
    st.subheader("🔍 Filters")
    col1, col2, col3 = st.columns([2, 1, 2])

    with col1:
        intents_sel = st.multiselect("Primary Intent", INTENTS, default=INTENTS)

    with col2:
        min_conf = st.slider("Min Confidence %", 0, 100, 0)

    with col3:
        search_query = st.text_input("🔎 Search keyword", "")

    # Apply filters
    fdf = filter_dataframe(df, intents_sel, min_conf, search_query)

    # Metrics
    _render_metrics(fdf)

    st.divider()

    # Display cards
    st.subheader("📇 Query Cards")
    for _, row in fdf.sort_values(
        by=["confidence_pct", "primary_intent"], ascending=[False, True]
    ).iterrows():
        color = INTENT_COLORS.get(row["primary_intent"], "#6b7280")
        badge_html = badge(row["primary_intent"], color)
        scores = json.loads(row["scores"])
        render_query_card(row, badge_html, scores)

    st.divider()

    # Data table
    _render_data_table(fdf)

    # Download button
    _render_download_button(fdf)


def _render_metrics(fdf):
    """Render metrics row."""
    st.divider()
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("📊 Total Queries", len(fdf))

    with c2:
        avg_conf = fdf["confidence_pct"].mean() if len(fdf) > 0 else 0
        st.metric("🎯 Avg Confidence", f"{avg_conf:.1f}%")

    with c3:
        success_count = int((fdf["status"] == "Success").sum()) if len(fdf) > 0 else 0
        st.metric("✅ Successful", success_count)

    with c4:
        error_count = int((fdf["status"] == "Error").sum()) if len(fdf) > 0 else 0
        st.metric("❌ Errors", error_count)


def _render_data_table(fdf):
    """Render data table."""
    st.subheader("📋 Data Table")
    st.dataframe(
        fdf,
        use_container_width=True,
        column_config={
            "confidence_pct": st.column_config.ProgressColumn(
                "Confidence %", max_value=100, format="%.1f%%"
            ),
            "reasoning": st.column_config.TextColumn("Reasoning", width="large"),
        },
    )


def _render_download_button(fdf):
    """Render CSV download button."""
    csv = fdf.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download CSV",
        csv,
        f"llm_intent_analysis_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        "text/csv",
        use_container_width=False,
    )
