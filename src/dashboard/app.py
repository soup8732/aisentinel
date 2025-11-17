from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple, Union
import os
import sys

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Ensure project root on sys.path for `src.*` imports even if launched elsewhere
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Ensure a writable Matplotlib cache location to avoid startup warnings
os.environ.setdefault("MPLCONFIGDIR", str((PROJECT_ROOT / ".mplconfig").resolve()))
(Path(os.environ["MPLCONFIGDIR"]).resolve()).mkdir(parents=True, exist_ok=True)

from src.utils.taxonomy import Category, tools_by_category

st.set_page_config(page_title="AISentinel Reviews", layout="wide")
st.title("AISentinel")
st.subheader("AI Tools Reviews & Ratings")
st.caption("Simple, clear insights into popularity and safety at a glance.")

EMOJI_POS = "😊"
EMOJI_MIX = "😐"
EMOJI_NEG = "😟"

# Build icon map resiliently across taxonomy versions
CATEGORY_ICON: Dict[str, str] = {}
try:
    if hasattr(Category, "CODE"):
        CATEGORY_ICON[getattr(Category, "CODE").value] = "💻"
    if hasattr(Category, "VIDEO_PIC"):
        CATEGORY_ICON[getattr(Category, "VIDEO_PIC").value] = "🎨"
    if hasattr(Category, "TEXT"):
        CATEGORY_ICON[getattr(Category, "TEXT").value] = "🧠"
    if hasattr(Category, "AUDIO"):
        CATEGORY_ICON[getattr(Category, "AUDIO").value] = "🎧"
    if hasattr(Category, "CODING"):
        CATEGORY_ICON[getattr(Category, "CODING").value] = "💻"
    if hasattr(Category, "VISION"):
        CATEGORY_ICON[getattr(Category, "VISION").value] = "👁️"
    if hasattr(Category, "NLP"):
        CATEGORY_ICON[getattr(Category, "NLP").value] = "🧠"
    if hasattr(Category, "GENERATIVE"):
        CATEGORY_ICON[getattr(Category, "GENERATIVE").value] = "🎨"
except Exception:
    CATEGORY_ICON = {}

# Friendly display labels for categories (fallback to title-case of raw value)
FRIENDLY_LABEL: Dict[str, str] = {
    "text": "Text & Chat",
    "video_pic": "Images & Video",
    "audio": "Audio & Speech",
    "code": "Coding & Dev",
    # Back-compat if older taxonomy values appear
    "coding_assistants": "Coding & Dev",
    "generative_image_video": "Images & Video",
    "nlp_llms": "Text & Chat",
    "vision_other": "Images & Video",
}

# Optional external links for known tools (extend as needed)
TOOL_LINKS: Dict[str, str] = {
    "ChatGPT": "https://chat.openai.com/",
    "Claude": "https://claude.ai/",
    "Gemini": "https://gemini.google.com/",
    "DeepSeek": "https://www.deepseek.com/",
    "Mistral": "https://mistral.ai/",
    "Bolt": "https://bolt.new/",
    "Loveable": "https://www.lovable.dev/",
    "Humain": "https://humane.com/",
}


@st.cache_data(show_spinner=False, ttl=3600)  # Cache for 1 hour, clear on restart
def load_dataset() -> pd.DataFrame:
    processed = Path("data/processed/sentiment.csv")
    if processed.exists():
        df = pd.read_csv(processed)
    else:
        now = pd.Timestamp.utcnow().normalize()
        rows = []
        tools_map = tools_by_category()
        for cat, names in tools_map.items():
            for i, tool in enumerate(names):  # include all tools from taxonomy
                for d in range(10):
                    ts = now - pd.Timedelta(days=9 - d)
                    score = ((hash(tool) + d) % 7 - 3) / 3.0
                    rows.append({
                        "created_at": ts,
                        "tool": tool,
                        "category": cat.value,
                        "score": max(-1.0, min(1.0, score)),
                        "label": "positive" if score > 0.2 else ("negative" if score < -0.2 else "neutral"),
                        "text": f"User mention about {tool}",
                    })
        df = pd.DataFrame(rows)
    if not pd.api.types.is_datetime64_any_dtype(df["created_at"]):
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    return df.dropna(subset=["created_at", "tool", "category"]).copy()


def score_to_010(x: float) -> int:
    x = max(-1.0, min(1.0, float(x)))
    return int(round((x + 1.0) * 5.0))


def sentiment_emoji(x: float) -> str:
    if x > 0.2:
        return EMOJI_POS
    if x < -0.2:
        return EMOJI_NEG
    return EMOJI_MIX


@st.cache_data(show_spinner=False, ttl=3600)  # Cache for 1 hour
def build_ratings(df: pd.DataFrame) -> pd.DataFrame:
    temp = df.copy()
    temp["is_pos"] = (temp["score"] > 0.2).astype(int)
    temp["is_neg"] = (temp["score"] < -0.2).astype(int)

    priv_kw = ["privacy", "security", "data", "breach", "leak", "unsafe"]
    temp["privacy_flag"] = temp["text"].astype(str).str.lower().apply(lambda t: any(k in t for k in priv_kw)).astype(int)

    agg = temp.groupby(["tool", "category"], as_index=False).agg(
        overall=("score", "mean"),
        n=("score", "count"),
        pos=("is_pos", "sum"),
        neg=("is_neg", "sum"),
        privacy=("privacy_flag", "mean"),
    )
    agg["perception"] = (agg["pos"] - agg["neg"]) / agg["n"].clip(lower=1)
    agg["privacy_score"] = 1.0 - agg["privacy"].clip(0, 1)

    agg["overall_10"] = agg["overall"].apply(score_to_010)
    agg["perception_10"] = agg["perception"].apply(score_to_010)
    agg["privacy_10"] = (agg["privacy_score"] * 10).round().astype(int)
    agg["mood"] = agg["overall"].apply(sentiment_emoji)
    # Friendly type label
    agg["type_label"] = agg["category"].apply(lambda v: FRIENDLY_LABEL.get(str(v), str(v).replace('_', ' ').title()))
    return agg


def search_and_filter(df_ratings: pd.DataFrame, df_raw: pd.DataFrame) -> Tuple[pd.DataFrame, int, str, Optional[Tuple[datetime, datetime]]]:
    # Quick jump to tool (autocomplete)
    all_tools = sorted(df_ratings["tool"].unique().tolist())
    selected_tool = st.selectbox(
        "🔍 Quick Jump to Tool",
        [""] + all_tools,
        placeholder="Type to search...",
        key="quick_search"
    )
    if selected_tool:
        st.session_state["selected_tool"] = selected_tool
        st.session_state["goto_details"] = True
        st.info(f"✨ Selected **{selected_tool}**. Switch to 'Details' tab to view.")

    st.divider()

    c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
    query = c1.text_input("Find AI tools...", placeholder="Search by name")
    # Build multi-map from friendly label -> list of raw categories present in the data
    raw_cats = sorted(df_ratings["category"].astype(str).unique().tolist())
    friendly_list = sorted({FRIENDLY_LABEL.get(c, c.replace('_',' ').title()) for c in raw_cats})
    label_to_raw: Dict[str, List[str]] = {}
    for rc in raw_cats:
        lbl = FRIENDLY_LABEL.get(rc, rc.replace('_',' ').title())
        label_to_raw.setdefault(lbl, []).append(rc)

    sel_labels = c2.multiselect("Type", friendly_list, default=friendly_list)
    selected_raw = [rc for lbl in sel_labels for rc in label_to_raw.get(lbl, [])]

    top_n = int(c3.selectbox("Show Top", [5, 10, 20, 50], index=1))
    view_mode = c4.radio("View", ["Table", "Cards"], horizontal=True)

    # Date filtering
    date_range = None
    if not df_raw.empty and "created_at" in df_raw.columns:
        with st.expander("📅 Filter by Date Range"):
            col_date1, col_date2 = st.columns(2)
            min_date = df_raw["created_at"].min().date()
            max_date = df_raw["created_at"].max().date()

            with col_date1:
                start_date = st.date_input("From", min_date, min_value=min_date, max_value=max_date)
            with col_date2:
                end_date = st.date_input("To", max_date, min_value=min_date, max_value=max_date)

            if start_date and end_date:
                date_range = (pd.Timestamp(start_date), pd.Timestamp(end_date))

    out = df_ratings[df_ratings["category"].isin(selected_raw)] if selected_raw else df_ratings
    if query.strip():
        out = out[out["tool"].str.contains(query.strip(), case=False, na=False)]
    return out, top_n, view_mode, date_range


def sidebar_tools(df: pd.DataFrame) -> None:
    """Sidebar utilities for cache clearing, navigation, and stats."""
    with st.sidebar:
        st.markdown("### 📊 Data Overview")

        # Data freshness indicators
        if not df.empty and "created_at" in df.columns:
            latest_date = df["created_at"].max()
            st.metric("Last Updated", latest_date.strftime("%Y-%m-%d %H:%M") if pd.notna(latest_date) else "N/A")

        st.metric("Total Data Points", f"{len(df):,}")
        st.metric("Tools Tracked", f"{df['tool'].nunique()}" if not df.empty else "0")

        if not df.empty and "category" in df.columns:
            st.metric("Categories", f"{df['category'].nunique()}")

        st.divider()

        # Score calculation explainer
        with st.expander("ℹ️ How Scores Work"):
            st.markdown("""
            **Overall Score** (0-10)
            - Average sentiment of all mentions
            - Range: -1 to +1, scaled to 0-10
            - Higher = more positive sentiment

            **User Perception** (0-10)
            - Ratio of positive vs negative mentions
            - Formula: (positive - negative) / total
            - Indicates user satisfaction

            **Privacy & Security** (0-10)
            - Based on privacy keyword mentions:
              - "privacy", "security", "data"
              - "breach", "leak", "unsafe"
            - Higher score = fewer concerns
            - 10/10 = no privacy issues mentioned
            """)

        st.divider()

        if st.button("🔄 Clear Cache & Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        st.caption("Click to refresh data and see new tools")


def get_trend_indicator(tool: str, df_raw: pd.DataFrame) -> str:
    """Get a simple trend indicator for a tool."""
    tool_data = df_raw[df_raw["tool"] == tool].copy()
    if tool_data.empty or len(tool_data) < 2 or "created_at" not in tool_data.columns:
        return "—"

    tool_data = tool_data.sort_values("created_at")
    recent_half = tool_data.tail(len(tool_data) // 2)
    older_half = tool_data.head(len(tool_data) // 2)

    if older_half.empty or recent_half.empty:
        return "—"

    recent_avg = recent_half["score"].mean()
    older_avg = older_half["score"].mean()

    diff = recent_avg - older_avg

    if diff > 0.1:
        return "📈 ↗"
    elif diff < -0.1:
        return "📉 ↘"
    else:
        return "➡ →"


def rankings_table(df: pd.DataFrame, top_n: int, df_raw: Optional[pd.DataFrame] = None) -> None:
    if df.empty:
        st.info("No results.")
        return
    view = (
        df.sort_values(["overall_10", "perception_10", "privacy_10"], ascending=[False, False, False])
        .head(top_n)
        .reset_index(drop=True)
    )
    view.insert(0, "#", view.index + 1)

    # Add trend indicator if raw data available
    if df_raw is not None:
        view["trend"] = view["tool"].apply(lambda t: get_trend_indicator(t, df_raw))
        cols = ["#", "tool", "mood", "trend", "overall_10", "perception_10", "privacy_10", "type_label", "n"]
    else:
        cols = ["#", "tool", "mood", "overall_10", "perception_10", "privacy_10", "type_label", "n"]

    view = view[cols]

    config = {
        "#": st.column_config.NumberColumn(width="small"),
        "tool": st.column_config.TextColumn("Tool", width="medium"),
        "mood": st.column_config.TextColumn("", width="small"),
        "overall_10": st.column_config.ProgressColumn("Overall", help="Overall sentiment 0-10", min_value=0, max_value=10),
        "perception_10": st.column_config.ProgressColumn("User Perception", min_value=0, max_value=10),
        "privacy_10": st.column_config.ProgressColumn("Privacy & Security", min_value=0, max_value=10),
        "type_label": st.column_config.TextColumn("Type"),
        "n": st.column_config.NumberColumn("Mentions", help="Sample size"),
    }

    if "trend" in cols:
        config["trend"] = st.column_config.TextColumn("Trend", help="Sentiment trend: ↗ improving, ↘ declining, → stable", width="small")

    st.dataframe(
        view,
        use_container_width=True,
        hide_index=True,
        column_config=config,
    )


def render_tool_card(row: pd.Series, key_scope: str, idx: int) -> None:
    icon = CATEGORY_ICON.get(str(row["category"]), "✨")
    emoji = row.get("mood", "")
    tool_name = str(row["tool"])
    with st.container(border=True):
        st.markdown(f"{icon}  **{tool_name}**  {emoji}")
        st.progress(int(row["overall_10"]) / 10.0, text=f"Overall {int(row['overall_10'])}/10")
        st.progress(int(row["perception_10"]) / 10.0, text=f"User Perception {int(row['perception_10'])}/10")
        st.progress(int(row["privacy_10"]) / 10.0, text=f"Privacy & Security {int(row['privacy_10'])}/10")
        cols = st.columns(2)
        with cols[0]:
            if st.button("View details", key=f"view-{key_scope}-{idx}-{tool_name}", use_container_width=True):
                st.session_state["selected_tool"] = tool_name
                st.session_state["show_details"] = True
                st.session_state["goto_details"] = True
                st.success(f"📋 Showing details for **{tool_name}**. Switch to 'Details' tab above.")
        with cols[1]:
            url = TOOL_LINKS.get(tool_name)
            if url:
                st.link_button("Open site", url)


def rankings_cards(df: pd.DataFrame, top_n: int, key_scope: str) -> None:
    if df.empty:
        st.info("No results.")
        return
    view = (
        df.sort_values(["overall_10", "perception_10", "privacy_10"], ascending=[False, False, False])
        .head(top_n)
        .reset_index(drop=True)
    )
    cols = st.columns(2)
    for i, (_, row) in enumerate(view.iterrows()):
        with cols[i % 2]:
            render_tool_card(row, key_scope, i)


def category_tabs(df: pd.DataFrame, top_n: int, view_mode: str, df_raw: Optional[pd.DataFrame] = None) -> None:
    labels = sorted(df["type_label"].unique().tolist())
    tabs = st.tabs([label for label in labels])
    for t, lbl in zip(tabs, labels):
        with t:
            sub = df[df["type_label"] == lbl]
            if view_mode == "Table":
                rankings_table(sub, top_n, df_raw)
            else:
                rankings_cards(sub, top_n, key_scope=f"cat-{lbl}")


def create_trend_chart(df: pd.DataFrame, tool_name: str) -> Optional[go.Figure]:
    """Create sentiment trend chart for a specific tool."""
    tool_data = df[df["tool"] == tool_name].copy()
    if tool_data.empty or "created_at" not in tool_data.columns:
        return None

    tool_data["date"] = tool_data["created_at"].dt.date
    daily_sentiment = tool_data.groupby("date")["score"].agg(["mean", "count"]).reset_index()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily_sentiment["date"],
        y=daily_sentiment["mean"],
        mode="lines+markers",
        name="Sentiment",
        line=dict(color="#1f77b4", width=2),
        marker=dict(size=6),
        hovertemplate="<b>%{x}</b><br>Sentiment: %{y:.2f}<br>Mentions: %{text}<extra></extra>",
        text=daily_sentiment["count"]
    ))

    fig.update_layout(
        title=f"{tool_name} Sentiment Trend",
        xaxis_title="Date",
        yaxis_title="Average Sentiment Score",
        hovermode="x unified",
        height=400,
        yaxis=dict(range=[-1, 1])
    )
    return fig


def create_sentiment_distribution_chart(df: pd.DataFrame, tool_name: Optional[str] = None) -> go.Figure:
    """Create sentiment distribution pie chart."""
    if tool_name:
        data = df[df["tool"] == tool_name]
        title = f"{tool_name} Sentiment Distribution"
    else:
        data = df
        title = "Overall Sentiment Distribution"

    sentiment_counts = data["label"].value_counts()

    colors = {"positive": "#2ecc71", "neutral": "#95a5a6", "negative": "#e74c3c"}
    fig = go.Figure(data=[go.Pie(
        labels=sentiment_counts.index,
        values=sentiment_counts.values,
        marker=dict(colors=[colors.get(label, "#3498db") for label in sentiment_counts.index]),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>"
    )])

    fig.update_layout(title=title, height=400)
    return fig


def create_category_comparison_chart(df_ratings: pd.DataFrame) -> go.Figure:
    """Create category comparison chart."""
    category_stats = df_ratings.groupby("type_label").agg({
        "overall_10": "mean",
        "perception_10": "mean",
        "privacy_10": "mean"
    }).reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Overall", x=category_stats["type_label"], y=category_stats["overall_10"]))
    fig.add_trace(go.Bar(name="Perception", x=category_stats["type_label"], y=category_stats["perception_10"]))
    fig.add_trace(go.Bar(name="Privacy", x=category_stats["type_label"], y=category_stats["privacy_10"]))

    fig.update_layout(
        title="Average Scores by Category",
        xaxis_title="Category",
        yaxis_title="Score (0-10)",
        barmode="group",
        height=400
    )
    return fig


def tool_comparison_section(df_ratings: pd.DataFrame, df_raw: pd.DataFrame) -> None:
    """Tool comparison interface."""
    st.markdown("### 🔍 Compare Tools Side-by-Side")

    col1, col2 = st.columns(2)
    all_tools = sorted(df_ratings["tool"].unique().tolist())

    with col1:
        tool_a = st.selectbox("Select Tool A", all_tools, key="compare_tool_a")
    with col2:
        tool_b = st.selectbox("Select Tool B", all_tools, index=min(1, len(all_tools)-1), key="compare_tool_b")

    if tool_a and tool_b and tool_a != tool_b:
        data_a = df_ratings[df_ratings["tool"] == tool_a].iloc[0]
        data_b = df_ratings[df_ratings["tool"] == tool_b].iloc[0]

        # Metrics comparison
        st.markdown("#### Score Comparison")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Overall",
                f"{tool_a}: {int(data_a['overall_10'])}/10",
                delta=int(data_a['overall_10'] - data_b['overall_10']),
                delta_color="normal"
            )
            st.caption(f"{tool_b}: {int(data_b['overall_10'])}/10")

        with col2:
            st.metric(
                "Perception",
                f"{tool_a}: {int(data_a['perception_10'])}/10",
                delta=int(data_a['perception_10'] - data_b['perception_10']),
                delta_color="normal"
            )
            st.caption(f"{tool_b}: {int(data_b['perception_10'])}/10")

        with col3:
            st.metric(
                "Privacy",
                f"{tool_a}: {int(data_a['privacy_10'])}/10",
                delta=int(data_a['privacy_10'] - data_b['privacy_10']),
                delta_color="normal"
            )
            st.caption(f"{tool_b}: {int(data_b['privacy_10'])}/10")

        # Bar chart comparison
        st.markdown("#### Visual Comparison")
        comparison_df = pd.DataFrame({
            "Metric": ["Overall", "Perception", "Privacy"],
            tool_a: [data_a["overall_10"], data_a["perception_10"], data_a["privacy_10"]],
            tool_b: [data_b["overall_10"], data_b["perception_10"], data_b["privacy_10"]]
        })

        fig = px.bar(
            comparison_df,
            x="Metric",
            y=[tool_a, tool_b],
            barmode="group",
            title=f"{tool_a} vs {tool_b}",
            color_discrete_sequence=["#1f77b4", "#ff7f0e"]
        )
        fig.update_layout(yaxis_title="Score (0-10)", yaxis=dict(range=[0, 10]))
        st.plotly_chart(fig, use_container_width=True)

        # Mention count comparison
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric(f"{tool_a} Mentions", int(data_a["n"]))
        with col_b:
            st.metric(f"{tool_b} Mentions", int(data_b["n"]))

    elif tool_a == tool_b:
        st.warning("Please select two different tools to compare.")


def details_panel(df_ratings: pd.DataFrame, df_raw: pd.DataFrame) -> None:
    tools = sorted(df_ratings["tool"].unique().tolist())
    
    # Show banner if tool was just selected from card
    if st.session_state.get("goto_details", False):
        selected = st.session_state.get("selected_tool")
        if selected and selected in tools:
            st.success(f"📋 **Showing details for {selected}** - Selected from card view")
            st.session_state["goto_details"] = False
    
    # Get selected tool from session state or default to first
    selected = st.session_state.get("selected_tool")
    default_idx = tools.index(selected) if selected and selected in tools else 0
    tool = st.selectbox("Select a tool", tools, index=default_idx, key="tool_select")
    
    # Update session state if user manually changes selection
    if tool != st.session_state.get("selected_tool"):
        st.session_state["selected_tool"] = tool
    
    item = df_ratings[df_ratings["tool"] == tool].iloc[0]
    icon = CATEGORY_ICON.get(str(item["category"]), "✨")
    
    st.markdown(f"### {icon} {tool}")
    st.divider()
    
    # Metrics row
    c1, c2, c3 = st.columns(3)
    c1.metric("Overall Score", f"{int(item['overall_10'])}/10", help="Overall sentiment score")
    c2.metric("User Perception", f"{int(item['perception_10'])}/10", help="How users feel about ease of use, reliability, features")
    c3.metric("Privacy & Security", f"{int(item['privacy_10'])}/10", help="Based on mentions of data handling, security, privacy concerns")
    
    # Progress bars
    st.markdown("#### Scores")
    st.progress(int(item["overall_10"]) / 10.0, text=f"Overall: {int(item['overall_10'])}/10")
    st.progress(int(item["perception_10"]) / 10.0, text=f"User Perception: {int(item['perception_10'])}/10")
    st.progress(int(item["privacy_10"]) / 10.0, text=f"Privacy & Security: {int(item['privacy_10'])}/10")
    
    # External link
    url = TOOL_LINKS.get(tool)
    if url:
        st.link_button("Visit tool website", url)
    
    st.divider()

    # Charts section
    st.markdown("#### 📊 Analytics")
    tab_trend, tab_dist = st.tabs(["Trend Over Time", "Sentiment Distribution"])

    with tab_trend:
        trend_chart = create_trend_chart(df_raw, tool)
        if trend_chart:
            st.plotly_chart(trend_chart, use_container_width=True)
        else:
            st.info("Not enough time-series data to show trends.")

    with tab_dist:
        dist_chart = create_sentiment_distribution_chart(df_raw, tool)
        st.plotly_chart(dist_chart, use_container_width=True)

    st.divider()
    st.markdown("#### 💬 What people are saying")
    sample = df_raw[df_raw["tool"] == tool].copy()
    if sample.empty:
        st.write("No recent mentions available in the current dataset.")
    else:
        pos = sample[sample["label"] == "positive"]["text"].astype(str).head(5).tolist()
        neg = sample[sample["label"] == "negative"]["text"].astype(str).head(5).tolist()
        neu = sample[sample["label"] == "neutral"]["text"].astype(str).head(3).tolist()

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Highlights (Positive)**")
            if pos:
                for t in pos:
                    st.write(f"• {t}")
            else:
                st.write("No positive highlights yet.")
        with col_b:
            st.markdown("**Concerns (Negative)**")
            if neg:
                for t in neg:
                    st.write(f"• {t}")
            else:
                st.write("No concerns mentioned yet.")

        if neu:
            st.markdown("**Neutral mentions**")
            for t in neu:
                st.write(f"• {t}")


# Load data and compute ratings
_df = load_dataset()
_ratings = build_ratings(_df)

# Sidebar tools (cache clear, etc.)
sidebar_tools(_df)

# Search/filter and top-N control + view toggle
_filtered, _top_n, _view_mode, _date_range = search_and_filter(_ratings, _df)

# Apply date filtering if specified
_filtered_df = _df.copy()
if _date_range and "created_at" in _df.columns:
    _filtered_df = _df[
        (_df["created_at"] >= _date_range[0]) &
        (_df["created_at"] <= _date_range[1])
    ]
    # Rebuild ratings with filtered data
    _filtered_ratings = build_ratings(_filtered_df)
    # Apply other filters
    if _filtered.empty:
        _display_ratings = _filtered_ratings
    else:
        # Merge filters - get tools from _filtered and data from _filtered_ratings
        _display_ratings = _filtered_ratings[_filtered_ratings["tool"].isin(_filtered["tool"])]
else:
    _filtered_df = _df
    _display_ratings = _filtered if not _filtered.empty else _ratings

# CSV Export Button
st.markdown("### 📥 Export Data")
col_exp1, col_exp2 = st.columns([1, 3])
with col_exp1:
    csv_ratings = _display_ratings.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Rankings (CSV)",
        data=csv_ratings,
        file_name=f"aisentinel_rankings_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )
with col_exp2:
    if not _filtered_df.empty:
        csv_raw = _filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Raw Data (CSV)",
            data=csv_raw,
            file_name=f"aisentinel_raw_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

# Tabs: Top Tools, By Type, Details, Analytics, Compare
st.divider()
_tabs = st.tabs(["Top Tools", "By Type", "Analytics", "Compare", "Details"])

with _tabs[0]:
    st.markdown("### 🏆 Top Rated AI Tools")
    if _view_mode == "Table":
        rankings_table(_display_ratings, _top_n, _filtered_df)
    else:
        rankings_cards(_display_ratings, _top_n, key_scope="top")

with _tabs[1]:
    st.markdown("### 📁 Browse by Type")
    category_tabs(_display_ratings, _top_n, _view_mode, _filtered_df)

with _tabs[2]:
    st.markdown("### 📊 Analytics & Insights")

    # Overall sentiment distribution
    st.markdown("#### Overall Sentiment Distribution")
    overall_dist = create_sentiment_distribution_chart(_filtered_df)
    st.plotly_chart(overall_dist, use_container_width=True)

    # Category comparison
    st.markdown("#### Category Performance")
    if not _display_ratings.empty:
        cat_chart = create_category_comparison_chart(_display_ratings)
        st.plotly_chart(cat_chart, use_container_width=True)

    # Top/Bottom performers
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🌟 Top 5 Tools")
        top_5 = _display_ratings.nlargest(5, "overall_10")[["tool", "overall_10", "n"]]
        st.dataframe(
            top_5.reset_index(drop=True),
            hide_index=True,
            column_config={
                "tool": "Tool",
                "overall_10": st.column_config.ProgressColumn("Score", min_value=0, max_value=10),
                "n": "Mentions"
            }
        )

    with col2:
        st.markdown("#### 📉 Bottom 5 Tools")
        bottom_5 = _display_ratings.nsmallest(5, "overall_10")[["tool", "overall_10", "n"]]
        st.dataframe(
            bottom_5.reset_index(drop=True),
            hide_index=True,
            column_config={
                "tool": "Tool",
                "overall_10": st.column_config.ProgressColumn("Score", min_value=0, max_value=10),
                "n": "Mentions"
            }
        )

with _tabs[3]:
    tool_comparison_section(_display_ratings, _filtered_df)

with _tabs[4]:
    st.markdown("### 🔍 Tool Details")
    details_panel(_display_ratings, _filtered_df)

st.divider()
st.caption("AISentinel — clear, friendly AI tool reviews powered by AI/ML. ")
