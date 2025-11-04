from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List, Optional

import pandas as pd
import plotly.express as px
import streamlit as st

try:
    from wordcloud import WordCloud  # type: ignore
except Exception:  # pragma: no cover
    WordCloud = None  # type: ignore

from src.utils.taxonomy import Category, tools_by_category

st.set_page_config(page_title="AISentinel Dashboard", layout="wide")
st.title("AISentinel Dashboard")
st.caption("Explore sentiment for AI tools across categories and time.")


@st.cache_data(show_spinner=False)
def load_dataset() -> pd.DataFrame:
    # Try processed CSV; otherwise synthesize a small demo dataset
    processed = Path("data/processed/sentiment.csv")
    if processed.exists():
        df = pd.read_csv(processed)
    else:
        now = pd.Timestamp.utcnow().normalize()
        rows = []
        tools_map = tools_by_category()
        for cat, names in tools_map.items():
            for i, tool in enumerate(names[:3]):
                for d in range(14):
                    ts = now - pd.Timedelta(days=13 - d)
                    score = ((i + d) % 5 - 2) / 2.0
                    rows.append({
                        "created_at": ts,
                        "tool": tool,
                        "category": cat.value,
                        "score": score,
                        "text": f"Sample mention about {tool} with score {score:+.2f}",
                        "label": "positive" if score > 0.2 else ("negative" if score < -0.2 else "neutral"),
                        "source": "demo",
                    })
        df = pd.DataFrame(rows)
    # Ensure types
    if not pd.api.types.is_datetime64_any_dtype(df["created_at"]):
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    return df.dropna(subset=["created_at", "tool", "category"])  # basic hygiene


def sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filters")
    categories = [c.value for c in Category]
    selected_categories = st.sidebar.multiselect("Categories", categories, default=categories)
    tools_available = sorted(df[df["category"].isin(selected_categories)]["tool"].unique().tolist())
    selected_tools = st.sidebar.multiselect("Tools", tools_available, default=tools_available[:5])

    min_date = df["created_at"].min().date()
    max_date = df["created_at"].max().date()
    start, end = st.sidebar.date_input("Date range", [min_date, max_date])  # type: ignore[assignment]

    filtered = df[
        (df["category"].isin(selected_categories))
        & (df["tool"].isin(selected_tools))
        & (df["created_at"].dt.date >= start)
        & (df["created_at"].dt.date <= end)
    ]
    return filtered


def sentiment_distribution(df: pd.DataFrame) -> None:
    st.subheader("Sentiment Distribution")
    fig = px.histogram(df, x="score", nbins=30, color="category", marginal="rug")
    st.plotly_chart(fig, use_container_width=True)


def time_series_trend(df: pd.DataFrame) -> None:
    st.subheader("Trends Over Time")
    ts = df.copy()
    ts["date"] = ts["created_at"].dt.date
    agg = ts.groupby(["date", "tool"], as_index=False)["score"].mean()
    fig = px.line(agg, x="date", y="score", color="tool")
    st.plotly_chart(fig, use_container_width=True)


def tool_comparison(df: pd.DataFrame) -> None:
    st.subheader("Tool Comparison")
    agg = df.groupby(["tool"], as_index=False)["score"].agg(["mean", "count"]).reset_index()
    agg.columns = ["tool", "mean", "count"]
    fig = px.bar(agg, x="tool", y="mean", hover_data=["count"], color="tool")
    st.plotly_chart(fig, use_container_width=True)


def word_clouds(df: pd.DataFrame) -> None:
    st.subheader("Top Positive/Negative Aspects")
    if WordCloud is None:
        st.info("Install `wordcloud` to enable this section.")
        return
    col1, col2 = st.columns(2)
    pos_text = " ".join(df[df["label"] == "positive"]["text"].astype(str).tolist())
    neg_text = " ".join(df[df["label"] == "negative"]["text"].astype(str).tolist())

    if pos_text:
        wc_pos = WordCloud(width=600, height=400, background_color="white").generate(pos_text)
        with col1:
            st.markdown("**Positive**")
            st.image(wc_pos.to_array(), use_column_width=True)
    if neg_text:
        wc_neg = WordCloud(width=600, height=400, background_color="white").generate(neg_text)
        with col2:
            st.markdown("**Negative**")
            st.image(wc_neg.to_array(), use_column_width=True)


# Load, filter, and render
_df = load_dataset()
filtered_df = sidebar_filters(_df)

sentiment_distribution(filtered_df)
time_series_trend(filtered_df)
tool_comparison(filtered_df)
word_clouds(filtered_df)
