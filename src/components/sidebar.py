# sidebar.py — Sidebar Configuration Component

import streamlit as st
from src.config.constants import __version__, AUTHOR, AVAILABLE_MODELS


def render_sidebar():
    """Render sidebar with configuration options."""
    st.header("⚙️ Settings")
    st.caption(f"Version: {__version__} • Author: {AUTHOR}")

    st.subheader("🤖 LLM Configuration")

    selected_model = st.selectbox(
        "Select Ollama Model",
        AVAILABLE_MODELS,
        index=0,
        help="Recommended: llama3.2:3b for best balance of speed and accuracy",
    )

    ollama_url = st.text_input(
        "Ollama API URL",
        "http://localhost:11434",
        help="Default: http://localhost:11434",
    )

    st.divider()

    _render_help_sections()

    return selected_model, ollama_url


def _render_help_sections():
    """Render help and about sections."""
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
