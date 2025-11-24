"""
Analyzer Factory
Handles analyzer initialization and caching
"""

import streamlit as st
from src.services.hybrid_analyzer import HybridIntentAnalyzer


@st.cache_resource
def get_analyzer(
    firecrawl_key: str,
    llm_model: str,
    llm_url: str,
    fc_weight: float,
    llm_weight: float,
    kw_weight: float,
) -> HybridIntentAnalyzer:
    """
    Get cached analyzer instance to avoid re-initialization.

    Args:
        firecrawl_key: Firecrawl API key
        llm_model: Ollama model name
        llm_url: Ollama API endpoint URL
        fc_weight: Firecrawl signal weight
        llm_weight: LLM signal weight
        kw_weight: Keyword signal weight

    Returns:
        Cached HybridIntentAnalyzer instance
    """
    return HybridIntentAnalyzer(
        firecrawl_api_key=firecrawl_key,
        llm_model=llm_model,
        llm_base_url=llm_url,
        firecrawl_weight=fc_weight,
        llm_weight=llm_weight,
        keyword_weight=kw_weight,
    )


def initialize_analyzer(config: dict) -> HybridIntentAnalyzer:
    """
    Initialize analyzer from configuration dictionary.

    Args:
        config: Configuration dictionary from sidebar

    Returns:
        Initialized HybridIntentAnalyzer instance

    Raises:
        Exception: If analyzer initialization fails
    """
    return get_analyzer(
        firecrawl_key=config["firecrawl_key"] if config["use_firecrawl"] else "",
        llm_model=config["llm_model"],
        llm_url=config["llm_url"],
        fc_weight=config["fc_weight"],
        llm_weight=config["llm_weight"],
        kw_weight=config["kw_weight"],
    )
