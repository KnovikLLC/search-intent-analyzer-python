"""
Analysis Tabs Component
Handles single and batch analysis UI tabs
"""

import streamlit as st
import pandas as pd
from typing import List

from src.services.hybrid_analyzer import HybridIntentAnalyzer
from src.components.result_display import (
    render_result_card,
    render_warning_messages,
    render_batch_summary,
    render_intent_distribution,
)


def analyze_batch(
    analyzer: HybridIntentAnalyzer, keywords: List[str], config: dict
) -> pd.DataFrame:
    """
    Analyze multiple keywords with progress tracking.

    Args:
        analyzer: HybridIntentAnalyzer instance
        keywords: List of keywords to analyze
        config: Configuration dictionary

    Returns:
        DataFrame with analysis results
    """
    results = []
    total = len(keywords)

    progress_bar = st.progress(0)
    status_text = st.empty()

    # Extract config once to avoid repeated dict lookups
    analyze_params = {
        "use_firecrawl": config["use_firecrawl"],
        "use_llm": config["use_llm"],
        "firecrawl_limit": config["fc_limit"],
        "firecrawl_country": config["fc_country"],
    }

    for i, keyword in enumerate(keywords, 1):
        status_text.text(f"Analyzing {i}/{total}: {keyword}")

        try:
            result = analyzer.analyze(keyword, **analyze_params)
            results.append(
                {
                    "Keyword": keyword,
                    "Primary Intent": result.primary_intent,
                    "Confidence": f"{result.confidence_score}%",
                    "Secondary Intent": result.secondary_intent,
                    "Mixed Intent": result.is_mixed_intent,
                    "Firecrawl Used": result.firecrawl_used,
                    "LLM Used": bool(result.llm_reasoning),
                    "SERP Features": ", ".join(result.serp_features) or "None",
                    "Reasoning": result.reasoning,
                    "LLM Explanation": result.llm_reasoning or "Not available",
                }
            )

        except Exception as e:
            results.append(
                {
                    "Keyword": keyword,
                    "Primary Intent": "Error",
                    "Confidence": "0%",
                    "Secondary Intent": "N/A",
                    "Mixed Intent": False,
                    "Firecrawl Used": False,
                    "LLM Used": False,
                    "SERP Features": f"Error: {str(e)}",
                    "Reasoning": f"Analysis failed: {str(e)}",
                    "LLM Explanation": "Not available",
                }
            )

        progress_bar.progress(i / total)

    status_text.text("✅ Analysis complete!")
    return pd.DataFrame(results)


def render_single_analysis_tab(analyzer: HybridIntentAnalyzer, config: dict):
    """
    Render single keyword analysis tab.

    Args:
        analyzer: HybridIntentAnalyzer instance
        config: Configuration dictionary
    """
    st.markdown("### Analyze Single Keyword")

    keyword = st.text_input(
        "Enter search keyword",
        placeholder="e.g., best noise cancelling headphones 2024",
        help="Enter any search query to analyze its intent",
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        analyze_button = st.button(
            "Analyze", type="primary", use_container_width=True
        )

    if analyze_button and keyword:
        with st.spinner("Analyzing intent..."):
            try:
                result = analyzer.analyze(
                    keyword,
                    use_firecrawl=config["use_firecrawl"],
                    use_llm=config["use_llm"],
                    firecrawl_limit=config["fc_limit"],
                    firecrawl_country=config["fc_country"],
                )

                st.success("✅ Analysis complete!")

                # Show warnings if needed
                render_warning_messages(config, result)

                # Display results
                render_result_card(result)

            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")


def render_batch_analysis_tab(analyzer: HybridIntentAnalyzer, config: dict):
    """
    Render batch analysis tab.

    Args:
        analyzer: HybridIntentAnalyzer instance
        config: Configuration dictionary
    """
    st.markdown("### Batch Analysis")

    keywords_input = st.text_area(
        "Enter keywords (one per line)",
        placeholder="how to learn python\nbest python courses\npython tutorial\npython documentation",
        height=200,
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        batch_button = st.button(
            "Analyze Batch", type="primary", use_container_width=True
        )

    if batch_button and keywords_input:
        keywords = [k.strip() for k in keywords_input.split("\n") if k.strip()]

        if keywords:
            st.info(f"Analyzing {len(keywords)} keywords...")

            df = analyze_batch(analyzer, keywords, config)

            # Display results table
            st.markdown("### 📋 Results")
            display_columns = [
                "Keyword",
                "Primary Intent",
                "Confidence",
                "Secondary Intent",
                "Firecrawl Used",
                "LLM Used",
            ]
            st.dataframe(df[display_columns], use_container_width=True)

            # Download button
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name="intent_analysis_results.csv",
                mime="text/csv",
            )

            # Summary statistics
            render_batch_summary(df)

            # Intent distribution chart
            render_intent_distribution(df)

            # Detailed results with reasoning for each keyword
            st.markdown("### 🧠 Detailed Analysis by Keyword")
            st.caption("Click on each keyword to see full reasoning and AI explanation")

            for idx, row in df.iterrows():
                with st.expander(
                    f"**{row['Keyword']}** - {row['Primary Intent']} ({row['Confidence']})"
                ):
                    st.markdown("**📊 Classification Details**")
                    st.write(f"**Primary Intent:** {row['Primary Intent']}")
                    st.write(f"**Confidence:** {row['Confidence']}")
                    st.write(f"**Secondary Intent:** {row['Secondary Intent']}")
                    st.markdown("---")
                    st.markdown("**💡 Classification Reasoning**")
                    st.info(row["Reasoning"])


def render_analysis_tabs(analyzer: HybridIntentAnalyzer, config: dict):
    """
    Render both analysis tabs.

    Args:
        analyzer: HybridIntentAnalyzer instance
        config: Configuration dictionary
    """
    tab1, tab2 = st.tabs(["🔍 Single Analysis", "📊 Batch Analysis"])

    with tab1:
        render_single_analysis_tab(analyzer, config)

    with tab2:
        render_batch_analysis_tab(analyzer, config)
