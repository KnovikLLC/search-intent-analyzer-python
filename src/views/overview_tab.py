# overview_tab.py — Overview Tab View

import streamlit as st
from src.components.charts import (
    create_intent_distribution_chart,
    create_confidence_histogram,
    create_confidence_boxplot,
)
from src.utils.data_processor import calculate_summary_stats


def render_overview_tab(df):
    """Render the overview tab with visualizations."""
    if df is None or df.empty:
        st.info("👈 Run an analysis to see visualizations.")
        return

    # Filter successful analyses
    viz_df = df[df["status"] == "Success"].copy()

    if len(viz_df) == 0:
        st.warning("No successful analyses to visualize.")
        return

    # Charts
    _render_charts(viz_df)

    # Summary statistics
    _render_summary_stats(viz_df)


def _render_charts(viz_df):
    """Render visualization charts."""
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🥧 Intent Distribution")
        counts = viz_df["primary_intent"].value_counts().reset_index()
        counts.columns = ["intent", "count"]
        fig1 = create_intent_distribution_chart(counts)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("📊 Confidence Distribution")
        fig2 = create_confidence_histogram(viz_df)
        st.plotly_chart(fig2, use_container_width=True)

    # Box plot
    st.subheader("📦 Confidence by Intent")
    fig3 = create_confidence_boxplot(viz_df)
    st.plotly_chart(fig3, use_container_width=True)


def _render_summary_stats(viz_df):
    """Render summary statistics table."""
    st.subheader("📈 Summary Statistics")
    summary_data = calculate_summary_stats(viz_df)
    st.dataframe(summary_data, use_container_width=True)
