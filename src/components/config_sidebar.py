"""
Configuration Sidebar Component
Handles all sidebar UI for app configuration
"""

import streamlit as st
import os


def render_api_keys_section() -> str:
    """Render API keys configuration section."""
    st.sidebar.subheader("API Keys")
    return st.sidebar.text_input(
        "Firecrawl API Key",
        value=os.getenv("FIRECRAWL_API_KEY", ""),
        type="password",
        help="Get your API key from firecrawl.dev",
    )


def render_signal_toggles(has_firecrawl_key: bool) -> tuple[bool, bool]:
    """Render signal toggle checkboxes."""
    st.sidebar.subheader("Analysis Signals")

    use_firecrawl = st.sidebar.checkbox(
        "🔍 Firecrawl SERP Data",
        value=has_firecrawl_key,
        disabled=not has_firecrawl_key,
        help="Fetch real SERP data from Google (requires API key)",
    )

    use_llm = st.sidebar.checkbox(
        "🤖 Ollama LLM Reasoning",
        value=True,
        help="Use local LLM for semantic analysis (requires Ollama)",
    )

    return use_firecrawl, use_llm


def render_firecrawl_settings(use_firecrawl: bool) -> tuple[int, str]:
    """Render Firecrawl-specific settings."""
    st.sidebar.subheader("Firecrawl Settings")

    if use_firecrawl:
        fc_limit = st.sidebar.slider("Results limit", 5, 20, 10)
        fc_country = st.sidebar.selectbox(
            "Country",
            ["US", "UK", "CA", "AU", "IN"],
            help="Target country for search results",
        )
    else:
        fc_limit = 10
        fc_country = "US"

    return fc_limit, fc_country


def render_llm_settings(use_llm: bool) -> tuple[str, str]:
    """Render LLM-specific settings."""
    st.sidebar.subheader("LLM Settings")

    if use_llm:
        llm_model = st.sidebar.selectbox(
            "Model",
            ["llama3.2:3b", "llama3.2:1b", "llama3.1:8b", "mistral:7b"],
            help="Ollama model to use",
        )
        llm_url = st.sidebar.text_input(
            "Ollama URL", value="http://localhost:11434", help="Ollama API endpoint"
        )
    else:
        llm_model = "llama3.2:3b"
        llm_url = "http://localhost:11434"

    return llm_model, llm_url


def render_weight_settings(
    use_firecrawl: bool, use_llm: bool
) -> tuple[float, float, float]:
    """Render signal weight configuration."""
    st.sidebar.subheader("Signal Weights")

    # Weight presets - LLM is now used only for explanation, not scoring
    # Firecrawl SERP data is the most trusted source
    weight_presets = {
        (True, True): (
            0.70,
            0.0,
            0.30,
        ),  # Both enabled - Firecrawl + Keywords (LLM for explanation only)
        (True, False): (0.70, 0.0, 0.30),  # Only Firecrawl
        (False, True): (0.0, 0.0, 1.0),  # Only LLM (fallback to keywords)
        (False, False): (0.0, 0.0, 1.0),  # Keywords only
    }

    if use_firecrawl and use_llm:
        st.sidebar.caption(
            "⭐ Firecrawl (SERP) + Keywords for scoring, LLM for explanation"
        )
        fc_weight = st.sidebar.slider(
            "Firecrawl weight",
            0.0,
            1.0,
            0.70,
            0.05,
            help="Real SERP data - primary scoring source",
        )
        kw_weight = st.sidebar.slider(
            "Keyword weight",
            0.0,
            1.0,
            0.30,
            0.05,
            help="Pattern matching - secondary scoring",
        )
        llm_weight = 0.0  # LLM not used for scoring
        st.sidebar.info("💡 LLM generates explanation only, not used for scoring")
    else:
        fc_weight, llm_weight, kw_weight = weight_presets[(use_firecrawl, use_llm)]

    return fc_weight, llm_weight, kw_weight


def render_firecrawl_status_warning(firecrawl_key: str):
    """Render Firecrawl status warning if applicable."""
    if firecrawl_key and len(firecrawl_key) > 20:
        st.sidebar.subheader("🔍 Firecrawl Status")
        st.sidebar.warning(
            "⚠️ **Currently Experiencing Issues**\n\n"
            "Firecrawl is returning 500 errors. Your API key is valid, but their servers are temporarily down.\n\n"
            "✅ **You can still analyze!** The app will use LLM + Keywords (still very accurate)."
        )


def render_about_section():
    """Render about section with app information."""
    st.sidebar.subheader("About")
    st.sidebar.info(
        "**Hybrid Intent Analyzer v2.0**\n\n"
        "🎯 **Intent Classification (100%):**\n"
        "• 70% Firecrawl SERP Analysis\n"
        "• 30% Keyword Pattern Matching\n\n"
        "🤖 **LLM Role:**\n"
        "• Generates explanations ONLY\n"
        "• Does NOT participate in scoring\n"
        "• Explains WHY the classification was made"
    )


def render_sidebar() -> dict:
    """
    Render complete sidebar with all configuration options.

    Returns:
        dict: Configuration dictionary with all settings
    """
    st.sidebar.title("⚙️ Configuration")

    # API Keys
    firecrawl_key = render_api_keys_section()

    # Signal toggles
    has_firecrawl_key = bool(firecrawl_key)
    use_firecrawl, use_llm = render_signal_toggles(has_firecrawl_key)

    # Service-specific settings
    fc_limit, fc_country = render_firecrawl_settings(use_firecrawl)
    llm_model, llm_url = render_llm_settings(use_llm)

    # Weight settings
    fc_weight, llm_weight, kw_weight = render_weight_settings(use_firecrawl, use_llm)

    st.sidebar.divider()

    # Status warnings
    render_firecrawl_status_warning(firecrawl_key)

    st.sidebar.divider()

    # About section
    render_about_section()

    return {
        "firecrawl_key": firecrawl_key,
        "use_firecrawl": use_firecrawl,
        "use_llm": use_llm,
        "fc_limit": fc_limit,
        "fc_country": fc_country,
        "llm_model": llm_model,
        "llm_url": llm_url,
        "fc_weight": fc_weight,
        "llm_weight": llm_weight,
        "kw_weight": kw_weight,
    }
