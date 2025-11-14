# app_llm.py — LLM-based Search Intent Analyzer (No Firecrawl Required)
# Version: 2.0.0
# Author: Knovik • Madusanka Premaratne (Madus)

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import json
import datetime as dt
import streamlit as st
import pandas as pd
import plotly.express as px

from src.config.constants import __version__, AUTHOR, INTENTS
from src.services.llm_intent_analyzer import LLMIntentAnalyzer, IntentResult

# Constants
INTENT_COLORS = {
    "Informational": "#2563eb",
    "Transactional": "#16a34a",
    "Navigational": "#f59e0b",
    "Commercial Investigation": "#ef4444",
}

CARD_CSS = """<style>
.badge{display:inline-block;padding:3px 10px;border-radius:999px;font-size:12px;font-weight:600;color:white}
.card{border:1px solid #e6e6e6;border-radius:14px;padding:14px 16px;margin-bottom:12px;background:#fff}
.card h4{margin:0 0 6px 0}
.kv{font-size:13px;color:#444}
.kv b{color:#111}
.smallmuted{color:#666;font-size:12px}
.reasoning{background:#f8f9fa;padding:10px;border-left:3px solid #2563eb;margin-top:8px;font-size:13px}
.score-bar{display:flex;align-items:center;margin:4px 0}
.score-label{width:180px;font-weight:500}
.score-progress{flex:1;height:20px;background:#e9ecef;border-radius:4px;overflow:hidden}
.score-fill{height:100%;background:#2563eb;transition:width 0.3s}
.score-value{width:60px;text-align:right;font-weight:600}
</style>"""

# Page config
st.set_page_config(
    page_title="LLM Search Intent Analyzer", page_icon="🤖", layout="wide"
)
st.markdown(CARD_CSS, unsafe_allow_html=True)


def badge(text, color):
    """Create a colored badge."""
    return f'<span class="badge" style="background:{color}">{text}</span>'


def hero_banner():
    """Display hero banner."""
    st.markdown(
        f"""<div style="text-align:center;padding:18px 8px;border-top:1px solid #e6e6e6;">
        <h2 style="margin:6px 0 10px 0;">🤖 LLM Search Intent Analyzer v{__version__}</h2>
        <p style="margin:6px 0 6px 0;">Built by <strong>{AUTHOR}</strong></p>
        <p style="margin:0;">Powered by <strong>Local LLM (Ollama)</strong> • No API Keys Required</p>
        </div>""",
        unsafe_allow_html=True,
    )


def app_footer():
    """Display footer."""
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


# Initialize app
hero_banner()

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Settings")
    st.caption(f"Version: {__version__} • Author: {AUTHOR}")

    st.subheader("🤖 LLM Configuration")

    # Model selection
    available_models = [
        "llama3.2:3b",
        "llama3.2:1b",
        "llama3.1:8b",
        "mistral:7b",
        "phi3:mini",
        "gemma2:2b",
    ]

    selected_model = st.selectbox(
        "Select Ollama Model",
        available_models,
        index=0,
        help="Recommended: llama3.2:3b for best balance of speed and accuracy",
    )

    ollama_url = st.text_input(
        "Ollama API URL",
        "http://localhost:11434",
        help="Default: http://localhost:11434",
    )

    st.divider()

    # Display help
    with st.expander("📖 Setup Instructions"):
        st.markdown(
            """
        **1. Install Ollama:**
        ```bash
        brew install ollama
        ```
        
        **2. Start Ollama Server:**
        ```bash
        ollama serve
        ```
        
        **3. Pull Model (in new terminal):**
        ```bash
        ollama pull llama3.2:3b
        ```
        
        **4. Verify Installation:**
        ```bash
        ollama list
        ```
        
        **Note:** First run may take time to download the model (~2GB)
        """
        )

    with st.expander("ℹ️ About This Tool"):
        st.markdown(
            """
        **LLM-Powered Intent Analysis:**
        - ✅ No API keys required
        - ✅ 100% local & private
        - ✅ Fast & accurate
        - ✅ No Firecrawl needed
        
        **How it works:**
        1. Enter search queries
        2. LLM analyzes user intent
        3. Get detailed results with reasoning
        """
        )


# Main tabs
tab_input, tab_results, tab_overview = st.tabs(["➊ Input", "➋ Results", "➌ Overview"])

# Tab 1: Input
with tab_input:
    st.subheader("Enter Search Queries")

    col1, col2 = st.columns([3, 1])

    with col1:
        kws_text = st.text_area(
            "One query per line",
            height=200,
            placeholder="Example:\nhow to train a dog\nbuy iPhone 15 pro\namazon login\nbest laptops 2024",
            help="Enter one search query per line. You can analyze up to 100 queries at once.",
        )

    with col2:
        st.info(
            f"""
        **Model:** {selected_model}
        
        **Features:**
        - AI-powered analysis
        - Detailed reasoning
        - Confidence scores
        - Batch processing
        """
        )

    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])

    with col_btn1:
        run_btn = st.button("🚀 Run Analysis", type="primary", use_container_width=True)

    with col_btn2:
        if st.button("📋 Load Examples", use_container_width=True):
            example_queries = """how to learn python programming
buy macbook pro 2024
facebook login page
best noise cancelling headphones
what is artificial intelligence
download spotify premium
apple official website
nike air max vs adidas ultraboost"""
            st.session_state["example_queries"] = example_queries
            st.rerun()

    # Load examples if clicked
    if "example_queries" in st.session_state:
        kws_text = st.session_state["example_queries"]
        st.session_state.pop("example_queries")


def run_analysis(queries: list, model: str, base_url: str):
    """Run LLM analysis for all queries."""
    try:
        analyzer = LLMIntentAnalyzer(model=model, base_url=base_url)
        results = []

        progress = st.progress(0, text="Initializing LLM analyzer...")

        for i, query in enumerate(queries, start=1):
            try:
                progress.progress(
                    i / len(queries),
                    text=f"Analyzing query {i}/{len(queries)}: {query[:40]}...",
                )

                result = analyzer.analyze(query)

                results.append(
                    {
                        "keyword": query,
                        "primary_intent": result.primary_intent,
                        "secondary_intent": result.secondary_intent,
                        "confidence_pct": result.confidence,
                        "reasoning": result.reasoning,
                        "scores": json.dumps(result.all_scores),
                        "status": "Success",
                    }
                )

            except Exception as e:
                results.append(
                    {
                        "keyword": query,
                        "primary_intent": "Error",
                        "secondary_intent": "Error",
                        "confidence_pct": 0.0,
                        "reasoning": f"Analysis failed: {str(e)}",
                        "scores": json.dumps({intent: 0.0 for intent in INTENTS}),
                        "status": "Error",
                    }
                )

        progress.empty()
        return pd.DataFrame(results)

    except Exception as e:
        st.error(f"❌ Failed to initialize analyzer: {str(e)}")
        return None


# Handle run button
if run_btn:
    kw_list = [k.strip() for k in (kws_text or "").splitlines() if k.strip()]
    kw_list = list(dict.fromkeys(kw_list))  # Remove duplicates

    if not kw_list:
        st.warning("⚠️ Please enter at least one search query.")
    elif len(kw_list) > 100:
        st.warning("⚠️ Maximum 100 queries allowed. Please reduce the number.")
    else:
        with st.spinner(
            f"🤖 Analyzing {len(kw_list)} queries with {selected_model}..."
        ):
            df = run_analysis(kw_list, selected_model, ollama_url)

            if df is not None:
                st.session_state["result_df"] = df
                st.success(
                    f"✅ Analysis complete! Processed {len(kw_list)} queries. See Results tab."
                )


# Tab 2: Results
with tab_results:
    df = st.session_state.get("result_df")

    if df is None or df.empty:
        st.info("👈 Run an analysis in the Input tab to see results here.")
    else:
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
        mask = df["primary_intent"].isin(intents_sel) & (
            df["confidence_pct"] >= min_conf
        )

        if search_query.strip():
            mask &= df["keyword"].str.contains(search_query, case=False, na=False)

        fdf = df[mask].copy()

        # Metrics
        st.divider()
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric("📊 Total Queries", len(fdf))

        with c2:
            avg_conf = fdf["confidence_pct"].mean() if len(fdf) > 0 else 0
            st.metric("🎯 Avg Confidence", f"{avg_conf:.1f}%")

        with c3:
            success_count = (
                int((fdf["status"] == "Success").sum()) if len(fdf) > 0 else 0
            )
            st.metric("✅ Successful", success_count)

        with c4:
            error_count = int((fdf["status"] == "Error").sum()) if len(fdf) > 0 else 0
            st.metric("❌ Errors", error_count)

        st.divider()

        # Display cards
        st.subheader("📇 Query Cards")

        for _, r in fdf.sort_values(
            by=["confidence_pct", "primary_intent"], ascending=[False, True]
        ).iterrows():
            color = INTENT_COLORS.get(r["primary_intent"], "#6b7280")
            badge_html = badge(r["primary_intent"], color)

            # Card HTML
            st.markdown(
                f"""<div class="card">
                <h4>{r["keyword"]} {badge_html}</h4>
                <div class="kv">
                    <b>Secondary:</b> {r["secondary_intent"]} • 
                    <b>Confidence:</b> {r["confidence_pct"]:.1f}%
                </div>
                <div class="reasoning">💭 <strong>Reasoning:</strong> {r["reasoning"]}</div>
                </div>""",
                unsafe_allow_html=True,
            )

            # Expandable details
            with st.expander("📊 View Detailed Scores"):
                scores = json.loads(r["scores"])
                st.markdown(score_bars_html(scores), unsafe_allow_html=True)

        st.divider()

        # Data table
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

        # Download button
        csv = fdf.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download CSV",
            csv,
            f"llm_intent_analysis_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "text/csv",
            use_container_width=False,
        )


# Tab 3: Overview
with tab_overview:
    df = st.session_state.get("result_df")

    if df is None or df.empty:
        st.info("👈 Run an analysis to see visualizations.")
    else:
        # Remove error rows for visualization
        viz_df = df[df["status"] == "Success"].copy()

        if len(viz_df) == 0:
            st.warning("No successful analyses to visualize.")
        else:
            col1, col2 = st.columns(2)

            with col1:
                # Intent distribution
                st.subheader("🥧 Intent Distribution")
                counts = viz_df["primary_intent"].value_counts().reset_index()
                counts.columns = ["intent", "count"]

                fig1 = px.pie(
                    counts,
                    names="intent",
                    values="count",
                    hole=0.45,
                    color="intent",
                    color_discrete_map=INTENT_COLORS,
                )
                fig1.update_traces(textposition="inside", textinfo="percent+label")
                st.plotly_chart(fig1, use_container_width=True)

            with col2:
                # Confidence distribution
                st.subheader("📊 Confidence Distribution")
                fig2 = px.histogram(
                    viz_df,
                    x="confidence_pct",
                    nbins=20,
                    labels={"confidence_pct": "Confidence %"},
                    color_discrete_sequence=["#2563eb"],
                )
                fig2.update_layout(showlegend=False)
                st.plotly_chart(fig2, use_container_width=True)

            # Box plot
            st.subheader("📦 Confidence by Intent")
            fig3 = px.box(
                viz_df,
                x="primary_intent",
                y="confidence_pct",
                color="primary_intent",
                color_discrete_map=INTENT_COLORS,
                labels={
                    "primary_intent": "Primary Intent",
                    "confidence_pct": "Confidence %",
                },
            )
            fig3.update_layout(showlegend=False)
            st.plotly_chart(fig3, use_container_width=True)

            # Summary stats
            st.subheader("📈 Summary Statistics")

            summary_data = (
                viz_df.groupby("primary_intent")
                .agg({"confidence_pct": ["mean", "min", "max", "count"]})
                .round(1)
            )

            summary_data.columns = [
                "Avg Confidence",
                "Min Confidence",
                "Max Confidence",
                "Count",
            ]
            summary_data = summary_data.reset_index()

            st.dataframe(summary_data, use_container_width=True)


# Footer
app_footer()
