# charts.py — Chart Components

import plotly.express as px
from src.config.constants import INTENT_COLORS


def create_intent_distribution_chart(counts_df):
    """Create pie chart for intent distribution."""
    fig = px.pie(
        counts_df,
        names="intent",
        values="count",
        hole=0.45,
        color="intent",
        color_discrete_map=INTENT_COLORS,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return fig


def create_confidence_histogram(df):
    """Create histogram for confidence distribution."""
    fig = px.histogram(
        df,
        x="confidence_pct",
        nbins=20,
        labels={"confidence_pct": "Confidence %"},
        color_discrete_sequence=["#2563eb"],
    )
    fig.update_layout(showlegend=False)
    return fig


def create_confidence_boxplot(df):
    """Create box plot for confidence by intent."""
    fig = px.box(
        df,
        x="primary_intent",
        y="confidence_pct",
        color="primary_intent",
        color_discrete_map=INTENT_COLORS,
        labels={
            "primary_intent": "Primary Intent",
            "confidence_pct": "Confidence %",
        },
    )
    fig.update_layout(showlegend=False)
    return fig
