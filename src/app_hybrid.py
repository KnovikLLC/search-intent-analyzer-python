"""
Hybrid Intent Analyzer App - Streamlit UI
Combines Firecrawl SERP data with Ollama LLM reasoning
Version: 2.0.0 - Refactored with modular components
"""

import sys
from pathlib import Path

# Add parent directory to path for module imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from dotenv import load_dotenv

from src.components.config_sidebar import render_sidebar
from src.components.analysis_tabs import render_analysis_tabs
from src.utils.analyzer_factory import initialize_analyzer


# Load environment
load_dotenv()

# Page config
st.set_page_config(
    page_title="Hybrid Intent Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
CUSTOM_CSS = """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e40af;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2rem;
    }
    .intent-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .signal-badge {
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.9rem;
        display: inline-block;
        margin: 0.2rem;
    }
    .signal-badge { background: #22c55e; }
    .signal-badge-inactive { background: #94a3b8; }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def main():
    """Main app function - orchestrates all components."""
    # Header
    st.markdown(
        '<p class="main-header">🎯 Hybrid Intent Analyzer</p>', unsafe_allow_html=True
    )
    st.markdown(
        '<p class="sub-header">SERP-Based Intent Classification with AI-Powered Explanations</p>',
        unsafe_allow_html=True,
    )

    # Render sidebar and get configuration
    config = render_sidebar()

    # Initialize analyzer with caching
    try:
        analyzer = initialize_analyzer(config)
    except Exception as e:
        st.error(f"Failed to initialize analyzer: {str(e)}")
        return

    # Render analysis tabs
    render_analysis_tabs(analyzer, config)


if __name__ == "__main__":
    main()
