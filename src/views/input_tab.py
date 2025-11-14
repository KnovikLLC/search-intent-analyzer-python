# input_tab.py — Input Tab View

import streamlit as st
from src.config.constants import EXAMPLE_QUERIES


def render_input_tab(selected_model: str):
    """Render the input tab for query entry."""
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
            st.session_state["example_queries"] = EXAMPLE_QUERIES
            st.rerun()

    # Load examples if clicked
    if "example_queries" in st.session_state:
        kws_text = st.session_state.pop("example_queries")

    return kws_text, run_btn
