# app_llm.py — LLM-based Search Intent Analyzer
# Version: 2.0.0
# Author: Knovik • Madusanka Premaratne (Madus)

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import streamlit as st
from src.config.constants import CARD_CSS
from src.components.ui_components import hero_banner, app_footer
from src.components.sidebar import render_sidebar
from src.views.input_tab import render_input_tab
from src.views.results_tab import render_results_tab
from src.views.overview_tab import render_overview_tab
from src.utils.data_processor import process_queries

# Page config
st.set_page_config(
    page_title="LLM Search Intent Analyzer", page_icon="🤖", layout="wide"
)
st.markdown(CARD_CSS, unsafe_allow_html=True)

# Initialize
hero_banner()

# Sidebar
with st.sidebar:
    selected_model, ollama_url = render_sidebar()

# Main tabs
tab_input, tab_results, tab_overview = st.tabs(["➊ Input", "➋ Results", "➌ Overview"])

# Tab 1: Input
with tab_input:
    kws_text, run_btn = render_input_tab(selected_model)

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
                try:
                    progress = st.progress(0, text="Initializing LLM analyzer...")

                    def update_progress(current, total, query):
                        progress.progress(
                            current / total,
                            text=f"Analyzing query {current}/{total}: {query[:40]}...",
                        )

                    df = process_queries(
                        kw_list, selected_model, ollama_url, update_progress
                    )
                    progress.empty()

                    if df is not None:
                        st.session_state["result_df"] = df
                        st.success(
                            f"✅ Analysis complete! Processed {len(kw_list)} queries. See Results tab."
                        )
                except Exception as e:
                    st.error(f"❌ Failed to run analysis: {str(e)}")

# Tab 2: Results
with tab_results:
    render_results_tab(st.session_state.get("result_df"))

# Tab 3: Overview
with tab_overview:
    render_overview_tab(st.session_state.get("result_df"))

# Footer
app_footer()
