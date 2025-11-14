# data_processor.py — Data Processing Logic

import json
import pandas as pd
from src.config.constants import INTENTS
from src.services.llm_intent_analyzer import LLMIntentAnalyzer


def process_queries(
    queries: list, model: str, base_url: str, progress_callback=None
) -> pd.DataFrame:
    """
    Process multiple queries and return results DataFrame.

    Args:
        queries: List of search queries to analyze
        model: LLM model name
        base_url: Ollama API URL
        progress_callback: Optional callback for progress updates

    Returns:
        DataFrame with analysis results
    """
    analyzer = LLMIntentAnalyzer(model=model, base_url=base_url)
    results = []

    for i, query in enumerate(queries, start=1):
        if progress_callback:
            progress_callback(i, len(queries), query)

        try:
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

    return pd.DataFrame(results)


def filter_dataframe(
    df: pd.DataFrame, intents: list, min_confidence: float, search_text: str
) -> pd.DataFrame:
    """
    Apply filters to the results dataframe.

    Args:
        df: Original dataframe
        intents: List of intents to include
        min_confidence: Minimum confidence threshold
        search_text: Text to search in keywords

    Returns:
        Filtered dataframe
    """
    mask = df["primary_intent"].isin(intents) & (df["confidence_pct"] >= min_confidence)

    if search_text.strip():
        mask &= df["keyword"].str.contains(search_text, case=False, na=False)

    return df[mask].copy()


def calculate_summary_stats(df: pd.DataFrame) -> dict:
    """Calculate summary statistics from results."""
    viz_df = df[df["status"] == "Success"]

    if len(viz_df) == 0:
        return {}

    summary = (
        viz_df.groupby("primary_intent")
        .agg({"confidence_pct": ["mean", "min", "max", "count"]})
        .round(1)
    )

    summary.columns = ["Avg Confidence", "Min Confidence", "Max Confidence", "Count"]
    return summary.reset_index()
