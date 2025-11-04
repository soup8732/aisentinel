from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple, Union
import os
import sys

import pandas as pd
import streamlit as st

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


@st.cache_data(show_spinner=False)
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


@st.cache_data(show_spinner=False)
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


def search_and_filter(df_ratings: pd.DataFrame) -> Tuple[pd.DataFrame, int, str]:
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

    out = df_ratings[df_ratings["category"].isin(selected_raw)] if selected_raw else df_ratings
    if query.strip():
        out = out[out["tool"].str.contains(query.strip(), case=False, na=False)]
    return out, top_n, view_mode


def rankings_table(df: pd.DataFrame, top_n: int) -> None:
    if df.empty:
        st.info("No results.")
        return
    view = (
        df.sort_values(["overall_10", "perception_10", "privacy_10"], ascending=[False, False, False])
        .head(top_n)
        .reset_index(drop=True)
    )
    view.insert(0, "#", view.index + 1)
    view = view[["#", "tool", "mood", "overall_10", "perception_10", "privacy_10", "type_label", "n"]]

    st.dataframe(
        view,
        use_container_width=True,
        hide_index=True,
        column_config={
            "#": st.column_config.NumberColumn(width="small"),
            "tool": st.column_config.TextColumn("Tool", width="medium"),
            "mood": st.column_config.TextColumn(""),
            "overall_10": st.column_config.ProgressColumn("Overall", help="Overall sentiment 0-10", min_value=0, max_value=10),
            "perception_10": st.column_config.ProgressColumn("User Perception", min_value=0, max_value=10),
            "privacy_10": st.column_config.ProgressColumn("Privacy & Security", min_value=0, max_value=10),
            "type_label": st.column_config.TextColumn("Type"),
            "n": st.column_config.NumberColumn("Mentions", help="Sample size"),
        },
    )


def render_tool_card(row: pd.Series, key_scope: str, idx: int) -> None:
    icon = CATEGORY_ICON.get(str(row["category"]), "✨")
    emoji = row.get("mood", "")
    with st.container(border=True):
        st.markdown(f"{icon}  **{row['tool']}**  {emoji}")
        st.progress(int(row["overall_10"]) / 10.0, text=f"Overall {int(row['overall_10'])}/10")
        st.progress(int(row["perception_10"]) / 10.0, text=f"User Perception {int(row['perception_10'])}/10")
        st.progress(int(row["privacy_10"]) / 10.0, text=f"Privacy & Security {int(row['privacy_10'])}/10")
        cols = st.columns(2)
        with cols[0]:
            if st.button("View details", key=f"view-{key_scope}-{idx}-{row['tool']}"):
                st.session_state["selected_tool"] = str(row["tool"])
                st.success("Details selected below.")
        with cols[1]:
            url = TOOL_LINKS.get(str(row["tool"]))
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


def category_tabs(df: pd.DataFrame, top_n: int, view_mode: str) -> None:
    labels = sorted(df["type_label"].unique().tolist())
    tabs = st.tabs([label for label in labels])
    for t, lbl in zip(tabs, labels):
        with t:
            sub = df[df["type_label"] == lbl]
            if view_mode == "Table":
                rankings_table(sub, top_n)
            else:
                rankings_cards(sub, top_n, key_scope=f"cat-{lbl}")


def details_panel(df_ratings: pd.DataFrame, df_raw: pd.DataFrame) -> None:
    tools = sorted(df_ratings["tool"].unique().tolist())
    default_tool = st.session_state.get("selected_tool") if st.session_state.get("selected_tool") in tools else None
    tool = st.selectbox("Select a tool", tools, index=(tools.index(default_tool) if default_tool else 0))
    item = df_ratings[df_ratings["tool"] == tool].iloc[0]

    c1, c2, c3 = st.columns(3)
    c1.metric("Overall", f"{int(item['overall_10'])}/10")
    c2.metric("User Perception", f"{int(item['perception_10'])}/10")
    c3.metric("Privacy & Security", f"{int(item['privacy_10'])}/10")

    url = TOOL_LINKS.get(tool)
    if url:
        st.link_button("Visit tool website", url)

    st.markdown("#### What people are saying")
    sample = df_raw[df_raw["tool"] == tool].copy()
    if sample.empty:
        st.write("No recent mentions available in the current dataset.")
    else:
        pos = sample[sample["label"] == "positive"]["text"].astype(str).head(3).tolist()
        neg = sample[sample["label"] == "negative"]["text"].astype(str).head(3).tolist()
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Highlights (Positive)**")
            for t in pos or ["No positive highlights yet."]:
                st.write(f"• {t}")
        with col_b:
            st.markdown("**Concerns (Negative)**")
            for t in neg or ["No concerns mentioned yet."]:
                st.write(f"• {t}")


# Load data and compute ratings
_df = load_dataset()
_ratings = build_ratings(_df)

# Search/filter and top-N control + view toggle
_filtered, _top_n, _view_mode = search_and_filter(_ratings)

# Tabs: Top Tools, By Type, Details
st.divider()
_tabs = st.tabs(["Top Tools", "By Type", "Details"])
with _tabs[0]:
    st.markdown("### Top Rated AI Tools")
    if _view_mode == "Table":
        rankings_table(_filtered if not _filtered.empty else _ratings, _top_n)
    else:
        rankings_cards(_filtered if not _filtered.empty else _ratings, _top_n, key_scope="top")

with _tabs[1]:
    st.markdown("### Browse by Type")
    category_tabs(_filtered if not _filtered.empty else _ratings, _top_n, _view_mode)

with _tabs[2]:
    st.markdown("### Tool Details")
    details_panel(_filtered if not _filtered.empty else _ratings, _df)

st.divider()
st.caption("AISentinel — clear, friendly AI tool reviews. ")
