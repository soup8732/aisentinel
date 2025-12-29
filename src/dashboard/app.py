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
from src.data_collection.artificialanalysis_client import ArtificialAnalysisClient, ModelInfo

st.set_page_config(
    page_title="AISentinel - AI Tools Reviews",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main header styling */
    .main-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    .main-header h1 {
        color: white !important;
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    .main-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.2rem;
    }

    /* Metric cards styling */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 600;
    }

    /* Better spacing */
    .block-container {
        padding-top: 3rem;
        padding-bottom: 3rem;
    }

    /* Card styling */
    .tool-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        margin-bottom: 1rem;
    }
    .tool-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-color: #667eea;
    }

    /* Button styling */
    .stButton>button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 500;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        font-weight: 500;
        border-radius: 8px;
    }

    /* Divider */
    hr {
        margin: 2rem 0;
        border-color: #e0e0e0;
    }

    /* GitHub link in header */
    .github-link {
        position: absolute;
        top: 1rem;
        right: 1.5rem;
        color: white;
        text-decoration: none;
        font-size: 1.5rem;
        opacity: 0.9;
        transition: all 0.3s ease;
    }
    .github-link:hover {
        opacity: 1;
        transform: scale(1.1);
    }
    .main-header {
        position: relative;
    }

    /* Responsive filter section */
    @media (max-width: 768px) {
        [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap;
        }
        [data-testid="stHorizontalBlock"] > div {
            min-width: 150px;
            flex: 1 1 45%;
        }
    }

    /* Prevent text truncation in selectbox and multiselect */
    .stSelectbox label, .stMultiSelect label, .stTextInput label, .stRadio label {
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: unset !important;
    }

    /* Better label visibility */
    .stSelectbox > label, .stMultiSelect > label, .stTextInput > label {
        font-size: 0.9rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <a href="https://github.com/soup8732/aisentinel" target="_blank" class="github-link" title="View on GitHub">
        <svg height="24" width="24" viewBox="0 0 16 16" fill="currentColor">
            <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
        </svg>
    </a>
    <h1>🤖 AISentinel</h1>
    <p>Real-time sentiment analysis of AI tools based on user feedback</p>
</div>
""", unsafe_allow_html=True)

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

# Mapping from tool names to ArtificialAnalysis company/creator names
TOOL_TO_COMPANY: Dict[str, str] = {
    "ChatGPT": "OpenAI",
    "DALL-E": "OpenAI",
    "Claude": "Anthropic",
    "Gemini": "Google",
    "DeepSeek": "DeepSeek",
    "Mistral": "Mistral AI",
    "GitHub Copilot": "GitHub",
    "CodeWhisperer": "Amazon",
    "Amazon Q Developer": "Amazon",
    "Stability AI": "Stability AI",
    "Midjourney": "Midjourney",
    "RunwayML": "Runway",
    "Adobe Firefly": "Adobe",
    "Whisper": "OpenAI",
    "ElevenLabs": "ElevenLabs",
    "Tabnine": "Tabnine",
    "Cursor": "Cursor",
    "Codeium": "Codeium",
    "Replit Ghostwriter": "Replit",
    "JetBrains AI Assistant": "JetBrains",
}


@st.cache_data(show_spinner=False, ttl=3600)  # Cache for 1 hour, clear on restart
def load_dataset() -> pd.DataFrame:
    """
    Load sentiment analysis data from CSV file.

    This function loads data from data/processed/sentiment.csv which should
    contain sentiment analysis results from the data collectors or the
    sample data generator script.

    Expected CSV columns:
    - created_at: When the mention was collected (will be converted to UTC)
    - tool: Name of the AI tool mentioned
    - category: Tool category (text, code, video_pic, audio)
    - score: Sentiment score from -1 (negative) to +1 (positive)
    - label: Sentiment label (positive/neutral/negative)
    - text: The actual user text/mention

    Returns:
        pd.DataFrame: Cleaned sentiment data ready for analysis

    Raises:
        FileNotFoundError: If no data file exists
    """
    processed = Path("data/processed/sentiment.csv")
    if not processed.exists():
        st.error("No data file found at data/processed/sentiment.csv")
        st.info("Generate sample data by running: `python scripts/generate_sample_data.py`")
        st.stop()

    df = pd.read_csv(processed)

    # Convert created_at to datetime
    if not pd.api.types.is_datetime64_any_dtype(df["created_at"]):
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")

    # Ensure timezone-aware (UTC) for consistent date filtering
    if df["created_at"].dt.tz is None:
        df["created_at"] = df["created_at"].dt.tz_localize("UTC")
    else:
        df["created_at"] = df["created_at"].dt.tz_convert("UTC")

    return df.dropna(subset=["created_at", "tool", "category"]).copy()


def score_to_010(x: float) -> int:
    """
    Convert sentiment score from [-1, +1] range to [0, 10] scale.

    Formula: score_010 = round((score + 1) * 5)
    Examples:
        -1.0 -> 0   (most negative)
         0.0 -> 5   (neutral)
        +1.0 -> 10  (most positive)

    Args:
        x: Sentiment score between -1 and +1

    Returns:
        int: Score on 0-10 scale for easy display
    """
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
    """
    Aggregate raw sentiment data into tool ratings.

    This function calculates three key scores for each AI tool:
    1. Overall Score: Average sentiment (-1 to +1, displayed as 0-10)
    2. Perception Score: Ratio of positive to negative mentions
    3. Privacy Score: Inverse of privacy-related keyword frequency

    Calculation Details:
    - Positive mention: score > 0.2
    - Negative mention: score < -0.2
    - Privacy keywords: privacy, security, data, breach, leak, unsafe

    Args:
        df: Raw sentiment DataFrame with columns: tool, category, score, text

    Returns:
        pd.DataFrame: Aggregated ratings with columns:
            - tool, category, type_label
            - overall_10, perception_10, privacy_10 (0-10 scales)
            - n (total mentions), pos (positive count), neg (negative count)
            - mood (emoji indicator)
    """
    temp = df.copy()
    # Flag positive mentions (score > 0.2)
    temp["is_pos"] = (temp["score"] > 0.2).astype(int)
    # Flag negative mentions (score < -0.2)
    temp["is_neg"] = (temp["score"] < -0.2).astype(int)

    # Flag mentions containing privacy-related keywords
    priv_kw = ["privacy", "security", "data", "breach", "leak", "unsafe"]
    temp["privacy_flag"] = temp["text"].astype(str).str.lower().apply(lambda t: any(k in t for k in priv_kw)).astype(int)

    # Aggregate by tool and category
    agg = temp.groupby(["tool", "category"], as_index=False).agg(
        overall=("score", "mean"),       # Average sentiment score
        n=("score", "count"),            # Total mentions
        pos=("is_pos", "sum"),           # Positive mention count
        neg=("is_neg", "sum"),           # Negative mention count
        privacy=("privacy_flag", "mean"), # Privacy keyword frequency
    )

    # Calculate perception: (positive - negative) / total mentions
    agg["perception"] = (agg["pos"] - agg["neg"]) / agg["n"].clip(lower=1)
    # Privacy score: higher is better (fewer privacy concerns)
    agg["privacy_score"] = 1.0 - agg["privacy"].clip(0, 1)

    # Convert to 0-10 scales for display
    agg["overall_10"] = agg["overall"].apply(score_to_010)
    agg["perception_10"] = agg["perception"].apply(score_to_010)
    agg["privacy_10"] = (agg["privacy_score"] * 10).round().astype(int)
    agg["mood"] = agg["overall"].apply(sentiment_emoji)
    # Friendly type label (e.g., "text_and_chat" -> "Text & Chat")
    agg["type_label"] = agg["category"].apply(lambda v: FRIENDLY_LABEL.get(str(v), str(v).replace('_', ' ').title()))
    return agg


def search_and_filter(df_ratings: pd.DataFrame, df_raw: pd.DataFrame) -> Tuple[pd.DataFrame, int, str, Optional[Tuple[datetime, datetime]]]:
    """
    Render search and filter controls, return filtered results.

    This function creates the sidebar controls for:
    1. Quick Jump: Autocomplete dropdown to navigate to any tool
    2. Text Search: Filter tools by name
    3. Category Filter: Multi-select for tool categories
    4. Top N: How many tools to display
    5. View Mode: Table or Card layout
    6. Date Range: Filter data by time period

    Args:
        df_ratings: Aggregated tool ratings DataFrame
        df_raw: Raw sentiment data DataFrame

    Returns:
        Tuple containing:
            - Filtered ratings DataFrame
            - Top N value (5, 10, 20, or 50)
            - View mode ("Table" or "Cards")
            - Date range tuple (start, end) or None
    """
    # Filters section with better organization
    st.markdown("### 🔍 Search & Filters")

    # Quick jump to tool (autocomplete) - prominent placement
    all_tools = sorted(df_ratings["tool"].unique().tolist())
    col_quick, col_spacer = st.columns([2, 1])
    with col_quick:
        selected_tool = st.selectbox(
            "Quick Jump to Tool",
            [""] + all_tools,
            placeholder="🔍 Type to search for a specific tool...",
            key="quick_search",
            help="Quickly navigate to a specific tool's details"
        )
        if selected_tool:
            st.session_state["selected_tool"] = selected_tool
            st.session_state["goto_details"] = True
            st.success(f"✨ **{selected_tool}** selected! Switch to 'Details' tab to view.")

    st.markdown("#### Filter Results")

    # Main filters in a cleaner layout - equal columns for better responsiveness
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        query = st.text_input(
            "Search by name",
            placeholder="🔎 Enter tool name...",
            help="Filter tools by name"
        )

    # Build multi-map from friendly label -> list of raw categories present in the data
    raw_cats = sorted(df_ratings["category"].astype(str).unique().tolist())
    friendly_list = sorted({FRIENDLY_LABEL.get(c, c.replace('_',' ').title()) for c in raw_cats})
    label_to_raw: Dict[str, List[str]] = {}
    for rc in raw_cats:
        lbl = FRIENDLY_LABEL.get(rc, rc.replace('_',' ').title())
        label_to_raw.setdefault(lbl, []).append(rc)

    with c2:
        sel_labels = st.multiselect(
            "Category",
            friendly_list,
            default=friendly_list,
            help="Filter by tool category"
        )
    selected_raw = [rc for lbl in sel_labels for rc in label_to_raw.get(lbl, [])]

    with c3:
        top_n = int(st.selectbox(
            "Show Top",
            [5, 10, 20, 50],
            index=1,
            help="Number of top tools to display"
        ))

    with c4:
        view_mode = st.radio(
            "View Mode",
            ["Table", "Cards"],
            horizontal=True,
            help="Switch between table and card view"
        )

    # Date filtering in collapsible section
    date_range = None
    if not df_raw.empty and "created_at" in df_raw.columns:
        with st.expander("📅 Advanced: Filter by Date Range", expanded=False):
            col_date1, col_date2 = st.columns(2)
            min_date = df_raw["created_at"].min().date()
            max_date = df_raw["created_at"].max().date()

            with col_date1:
                start_date = st.date_input(
                    "From Date",
                    min_date,
                    min_value=min_date,
                    max_value=max_date,
                    help="Start date for filtering"
                )
            with col_date2:
                end_date = st.date_input(
                    "To Date",
                    max_date,
                    min_value=min_date,
                    max_value=max_date,
                    help="End date for filtering"
                )

            if start_date and end_date:
                # Make timestamps timezone-aware to match DataFrame
                date_range = (
                    pd.Timestamp(start_date).tz_localize('UTC'),
                    pd.Timestamp(end_date).tz_localize('UTC') + pd.Timedelta(days=1)
                )
                # Ensure timezone-aware timestamps to match dataframe (date objects are naive)
                start_ts = pd.Timestamp(start_date).tz_localize('UTC')
                end_ts = pd.Timestamp(end_date).tz_localize('UTC')
                date_range = (start_ts, end_ts)

    out = df_ratings[df_ratings["category"].isin(selected_raw)] if selected_raw else df_ratings
    if query.strip():
        out = out[out["tool"].str.contains(query.strip(), case=False, na=False)]
    return out, top_n, view_mode, date_range


def sidebar_tools(df: pd.DataFrame) -> None:
    """Sidebar utilities for cache clearing, navigation, and stats."""
    with st.sidebar:
        # Branding
        st.markdown("---")

        st.markdown("### 📊 Dashboard Stats")

        # Data freshness indicators with better formatting
        if not df.empty and "created_at" in df.columns:
            latest_date = df["created_at"].max()
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown("🕐")
            with col2:
                st.markdown(f"**Updated**<br>{latest_date.strftime('%b %d, %Y') if pd.notna(latest_date) else 'N/A'}", unsafe_allow_html=True)

        # Metrics in a cleaner format
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📝 Data Points", f"{len(df):,}")
        with col2:
            st.metric("🛠️ Tools", f"{df['tool'].nunique()}" if not df.empty else "0")

        if not df.empty and "category" in df.columns:
            st.metric("📁 Categories", f"{df['category'].nunique()}")

        st.markdown("---")

        # Score calculation explainer with better formatting
        with st.expander("💡 How Scores Work", expanded=False):
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
    """
    Calculate sentiment trend for a tool (improving, declining, or stable).

    Compares average sentiment of recent mentions vs older mentions:
    - Splits data in half chronologically
    - Calculates average score for each half
    - Returns emoji indicator based on the difference

    Thresholds:
        - diff > 0.1: Improving (📈 ↗)
        - diff < -0.1: Declining (📉 ↘)
        - otherwise: Stable (➡ →)

    Args:
        tool: Name of the AI tool
        df_raw: Raw sentiment DataFrame

    Returns:
        str: Emoji indicator (📈 ↗, 📉 ↘, or ➡ →)
    """
    tool_data = df_raw[df_raw["tool"] == tool].copy()
    if tool_data.empty or len(tool_data) < 2 or "created_at" not in tool_data.columns:
        return "—"

    # Sort chronologically and split in half
    tool_data = tool_data.sort_values("created_at")
    recent_half = tool_data.tail(len(tool_data) // 2)
    older_half = tool_data.head(len(tool_data) // 2)

    if older_half.empty or recent_half.empty:
        return "—"

    # Compare average sentiment of recent vs older mentions
    recent_avg = recent_half["score"].mean()
    older_avg = older_half["score"].mean()

    diff = recent_avg - older_avg

    # Return appropriate trend indicator
    if diff > 0.1:
        return "📈 ↗"  # Improving
    elif diff < -0.1:
        return "📉 ↘"  # Declining
    else:
        return "➡ →"   # Stable


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


@st.dialog("Tool Details")
def show_tool_details_modal(tool_name: str, row: pd.Series, df_raw: pd.DataFrame):
    """Display tool details in a modal dialog with model selection and technical metrics."""
    icon = CATEGORY_ICON.get(str(row["category"]), "✨")

    st.markdown(f"# {icon} {tool_name}")

    # Category badge
    category_label = row.get("type_label", "")
    if category_label:
        st.markdown(f"**Category:** {category_label}")

    st.markdown("---")

    # SENTIMENT METRICS SECTION
    st.markdown("### 💭 User Sentiment Analysis")
    overall_score = int(row["overall_10"])
    perception_score = int(row["perception_10"])
    privacy_score = int(row["privacy_10"])

    def get_score_color(score):
        if score >= 7:
            return "#10b981"
        elif score >= 5:
            return "#f59e0b"
        else:
            return "#ef4444"

    # Sentiment scores display
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div style='text-align:center; padding:15px; background:#f8f9fa; border-radius:10px;'><div style='font-size:2.5em; font-weight:bold; color:{get_score_color(overall_score)};'>{overall_score}</div><div style='font-size:0.9em; color:#666; margin-top:8px;'>Overall Sentiment</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div style='text-align:center; padding:15px; background:#f8f9fa; border-radius:10px;'><div style='font-size:2.5em; font-weight:bold; color:{get_score_color(perception_score)};'>{perception_score}</div><div style='font-size:0.9em; color:#666; margin-top:8px;'>User Perception</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div style='text-align:center; padding:15px; background:#f8f9fa; border-radius:10px;'><div style='font-size:2.5em; font-weight:bold; color:{get_score_color(privacy_score)};'>{privacy_score}</div><div style='font-size:0.9em; color:#666; margin-top:8px;'>Privacy & Security</div></div>", unsafe_allow_html=True)

    # Sentiment stats
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Total Mentions", f"{int(row['n']):,}")
        st.metric("Positive Reviews", f"{int(row['pos']):,}")
    with col_b:
        st.metric("Category Rank", "Top 10%", help="Estimated ranking within category")
        st.metric("Negative Reviews", f"{int(row['neg']):,}")

    st.markdown("---")

    # TECHNICAL METRICS SECTION (from ArtificialAnalysis API)
    st.markdown("### 🔬 Technical Metrics & Model Information")
    
    # Get company name for API lookup
    company_name = TOOL_TO_COMPANY.get(tool_name)
    
    if company_name:
        try:
            # Initialize API client
            api_client = ArtificialAnalysisClient()
            
            # Fetch models from this company
            with st.spinner(f"Loading models from {company_name}..."):
                company_models = api_client.get_models_by_creator(company_name)
            
            if company_models:
                # Model selection dropdown
                model_options = {f"{m.name} ({m.slug or m.id[:8]})": m for m in company_models}
                model_names = list(model_options.keys())
                
                if model_names:
                    selected_model_key = st.selectbox(
                        f"Select a specific model from {company_name}",
                        model_names,
                        key=f"model_select_{tool_name}",
                        help="Choose a specific model to view detailed technical metrics"
                    )
                    
                    selected_model: ModelInfo = model_options[selected_model_key]
                    
                    # Display technical metrics
                    st.markdown(f"#### 📊 {selected_model.name} Technical Specifications")
                    
                    # Two-column layout for metrics
                    tech_col1, tech_col2 = st.columns(2)
                    
                    with tech_col1:
                        # Evaluations/Benchmarks
                        if selected_model.evaluations:
                            st.markdown("**📈 Evaluation Scores**")
                            eval_data = selected_model.evaluations
                            
                            # Display key metrics
                            key_metrics = [
                                ("artificial_analysis_intelligence_index", "Intelligence Index"),
                                ("artificial_analysis_coding_index", "Coding Index"),
                                ("artificial_analysis_math_index", "Math Index"),
                                ("mmlu_pro", "MMLU Pro"),
                                ("gpqa", "GPQA"),
                                ("math_500", "Math 500"),
                            ]
                            
                            for key, label in key_metrics:
                                if key in eval_data:
                                    value = eval_data[key]
                                    if isinstance(value, (int, float)):
                                        if key.endswith("_index"):
                                            # Index scores (0-100 scale typically)
                                            st.metric(label, f"{value:.1f}", help=f"{key}")
                                        else:
                                            # Ratio scores (0-1 scale)
                                            st.metric(label, f"{value:.3f}", help=f"{key}")
                    
                    with tech_col2:
                        # Pricing information
                        if selected_model.pricing:
                            st.markdown("**💰 Pricing**")
                            pricing = selected_model.pricing
                            
                            if "price_1m_input_tokens" in pricing:
                                st.metric(
                                    "Input Tokens",
                                    f"${pricing['price_1m_input_tokens']:.2f}/1M",
                                    help="Price per million input tokens"
                                )
                            if "price_1m_output_tokens" in pricing:
                                st.metric(
                                    "Output Tokens",
                                    f"${pricing['price_1m_output_tokens']:.2f}/1M",
                                    help="Price per million output tokens"
                                )
                            if "price_1m_blended_3_to_1" in pricing:
                                st.metric(
                                    "Blended (3:1)",
                                    f"${pricing['price_1m_blended_3_to_1']:.2f}/1M",
                                    help="Blended pricing (3 input : 1 output ratio)"
                                )
                        
                        # Performance metrics
                        if selected_model.median_output_tokens_per_second is not None:
                            st.markdown("**⚡ Performance**")
                            st.metric(
                                "Output Speed",
                                f"{selected_model.median_output_tokens_per_second:.1f} tokens/sec",
                                help="Median output generation speed"
                            )
                            if selected_model.median_time_to_first_token_seconds is not None:
                                st.metric(
                                    "Time to First Token",
                                    f"{selected_model.median_time_to_first_token_seconds:.2f}s",
                                    help="Median time to first token"
                                )
                    
                    # Additional evaluation metrics in expander
                    if selected_model.evaluations and len(selected_model.evaluations) > 6:
                        with st.expander("📋 All Evaluation Metrics"):
                            eval_df = pd.DataFrame([
                                {"Metric": k.replace("_", " ").title(), "Score": v}
                                for k, v in selected_model.evaluations.items()
                            ])
                            st.dataframe(eval_df, use_container_width=True, hide_index=True)
                
                else:
                    st.info(f"Found models from {company_name}, but no models available to display.")
            else:
                st.info(f"No models found for {company_name} in ArtificialAnalysis database. The company may use different naming or may not be tracked yet.")
        
        except ValueError as e:
            # API key not configured
            st.warning("⚠️ **API Key Not Configured**")
            st.info(f"To view technical metrics, add your `AA_API_KEY` to the `.env` file. Visit https://artificialanalysis.ai/ to get an API key.")
            st.caption(str(e))
        
        except Exception as e:
            # Other API errors
            st.warning("⚠️ **Unable to Load Technical Metrics**")
            st.info(f"Error connecting to ArtificialAnalysis API: {str(e)}")
            st.caption("Technical metrics are optional and won't affect sentiment analysis.")
    else:
        st.info(f"💡 **Model Information Available**")
        st.caption(f"To view technical metrics for {tool_name}, we need to map it to a company name in the ArtificialAnalysis database. This feature is being expanded.")

    st.markdown("---")

    # External link
    url = TOOL_LINKS.get(tool_name)
    if url:
        st.markdown("### 🔗 Official Website")
        st.link_button(f"Visit {tool_name}", url, use_container_width=True, type="primary")

    # Charts if data available
    if not df_raw.empty:
        st.markdown("---")
        st.markdown("### 📈 Sentiment Analysis")

        tab1, tab2 = st.tabs(["Trend Over Time", "Distribution"])

        with tab1:
            trend_chart = create_trend_chart(df_raw, tool_name)
            if trend_chart:
                st.plotly_chart(trend_chart, use_container_width=True)
            else:
                st.info("Not enough historical data for trend analysis")

        with tab2:
            dist_chart = create_sentiment_distribution_chart(df_raw, tool_name)
            st.plotly_chart(dist_chart, use_container_width=True)

    # User feedback samples
    st.markdown("---")
    st.markdown("### 💬 What Users Are Saying")

    tool_data = df_raw[df_raw["tool"] == tool_name]
    if not tool_data.empty:
        pos = tool_data[tool_data["label"] == "positive"]["text"].astype(str).head(3).tolist()
        neg = tool_data[tool_data["label"] == "negative"]["text"].astype(str).head(3).tolist()

        col_pos, col_neg = st.columns(2)
        with col_pos:
            st.markdown("**😊 Positive Feedback**")
            if pos:
                for comment in pos:
                    st.markdown(f"• *{comment}*")
            else:
                st.info("No positive feedback available")

        with col_neg:
            st.markdown("**😟 Concerns**")
            if neg:
                for comment in neg:
                    st.markdown(f"• *{comment}*")
            else:
                st.info("No negative feedback available")
    else:
        st.info("No user feedback available in current dataset")


def render_tool_card(row: pd.Series, key_scope: str, idx: int, df_raw: Optional[pd.DataFrame] = None) -> None:
    icon = CATEGORY_ICON.get(str(row["category"]), "✨")
    emoji = row.get("mood", "")
    tool_name = str(row["tool"])
    category_label = row.get("type_label", "")

    with st.container(border=True):
        # Header with tool name and category
        col_name, col_badge = st.columns([3, 1])
        with col_name:
            st.markdown(f"### {icon} {tool_name} {emoji}")
        with col_badge:
            if category_label:
                st.markdown(f"<div style='text-align:right; padding-top:10px;'><span style='background:#f0f2f6; padding:4px 12px; border-radius:12px; font-size:0.8em;'>{category_label}</span></div>", unsafe_allow_html=True)

        st.markdown("---")

        # Scores with color coding
        overall_score = int(row["overall_10"])
        perception_score = int(row["perception_10"])
        privacy_score = int(row["privacy_10"])

        # Score color helper
        def get_score_color(score):
            if score >= 7:
                return "#10b981"  # green
            elif score >= 5:
                return "#f59e0b"  # orange
            else:
                return "#ef4444"  # red

        # Display scores with better formatting
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"<div style='text-align:center;'><div style='font-size:2em; font-weight:bold; color:{get_score_color(overall_score)};'>{overall_score}</div><div style='font-size:0.8em; color:#666;'>Overall</div></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div style='text-align:center;'><div style='font-size:2em; font-weight:bold; color:{get_score_color(perception_score)};'>{perception_score}</div><div style='font-size:0.8em; color:#666;'>Perception</div></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div style='text-align:center;'><div style='font-size:2em; font-weight:bold; color:{get_score_color(privacy_score)};'>{privacy_score}</div><div style='font-size:0.8em; color:#666;'>Privacy</div></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Action buttons
        cols = st.columns(2)
        with cols[0]:
            if st.button("📊 View Details", key=f"view-{key_scope}-{idx}-{tool_name}", use_container_width=True, type="primary"):
                if df_raw is not None:
                    show_tool_details_modal(tool_name, row, df_raw)
                else:
                    st.warning("Details temporarily unavailable")
        with cols[1]:
            url = TOOL_LINKS.get(tool_name)
            if url:
                st.link_button("🔗 Website", url, use_container_width=True)
            else:
                st.markdown("<div style='height:38px;'></div>", unsafe_allow_html=True)  # Placeholder spacing


def rankings_cards(df: pd.DataFrame, top_n: int, key_scope: str, df_raw: Optional[pd.DataFrame] = None) -> None:
    if df.empty:
        st.info("🔍 No tools match your current filters. Try adjusting your search criteria.")
        return

    view = (
        df.sort_values(["overall_10", "perception_10", "privacy_10"], ascending=[False, False, False])
        .head(top_n)
        .reset_index(drop=True)
    )

    # Show results count
    st.markdown(f"*Showing top {len(view)} of {len(df)} tools*")
    st.markdown("")

    cols = st.columns(2)
    for i, (_, row) in enumerate(view.iterrows()):
        with cols[i % 2]:
            render_tool_card(row, key_scope, i, df_raw)


def category_tabs(df: pd.DataFrame, top_n: int, view_mode: str, df_raw: Optional[pd.DataFrame] = None) -> None:
    labels = sorted(df["type_label"].unique().tolist())
    tabs = st.tabs([label for label in labels])
    for t, lbl in zip(tabs, labels):
        with t:
            sub = df[df["type_label"] == lbl]
            if view_mode == "Table":
                rankings_table(sub, top_n, df_raw)
            else:
                rankings_cards(sub, top_n, key_scope=f"cat-{lbl}", df_raw=df_raw)


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
    # Ensure both sides of comparison are timezone-aware (date_range is already UTC from search_and_filter)
    start_date = _date_range[0]
    end_date = _date_range[1]
    _filtered_df = _df[
        (_df["created_at"] >= start_date) &
        (_df["created_at"] <= end_date)
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

# CSV Export Section
with st.expander("📥 Export Data", expanded=False):
    st.markdown("Download the current results as CSV files for further analysis.")
    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        csv_ratings = _display_ratings.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📊 Download Rankings (CSV)",
            data=csv_ratings,
            file_name=f"aisentinel_rankings_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary"
        )
        st.caption(f"{len(_display_ratings)} tools in rankings")
    with col_exp2:
        if not _filtered_df.empty:
            csv_raw = _filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📝 Download Raw Data (CSV)",
                data=csv_raw,
                file_name=f"aisentinel_raw_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            st.caption(f"{len(_filtered_df)} data points")

# Main Content Tabs
st.divider()
st.markdown("## 📊 Explore AI Tools")
_tabs = st.tabs(["🏆 Top Tools", "📁 By Category", "📈 Analytics", "⚖️ Compare", "🔍 Details"])

with _tabs[0]:
    st.markdown("### 🏆 Top Rated AI Tools")
    st.markdown("*Discover the highest-rated AI tools based on real user sentiment*")
    st.markdown("")
    if _view_mode == "Table":
        rankings_table(_display_ratings, _top_n, _filtered_df)
    else:
        rankings_cards(_display_ratings, _top_n, key_scope="top", df_raw=_filtered_df)

with _tabs[1]:
    st.markdown("### 📁 Browse by Category")
    st.markdown("*Explore AI tools organized by their primary function*")
    st.markdown("")
    category_tabs(_display_ratings, _top_n, _view_mode, _filtered_df)

with _tabs[2]:
    st.markdown("### 📈 Analytics & Insights")
    st.markdown("*Deep dive into sentiment patterns and performance metrics*")
    st.markdown("")

    # Overall sentiment distribution
    st.markdown("#### 📊 Sentiment Distribution")
    overall_dist = create_sentiment_distribution_chart(_filtered_df)
    st.plotly_chart(overall_dist, use_container_width=True)

    st.markdown("---")

    # Category comparison
    st.markdown("#### 📁 Category Performance Comparison")
    if not _display_ratings.empty:
        cat_chart = create_category_comparison_chart(_display_ratings)
        st.plotly_chart(cat_chart, use_container_width=True)
    else:
        st.info("No data available for category comparison.")

    st.markdown("---")

    # Top/Bottom performers
    st.markdown("#### 🏅 Performance Leaders & Laggards")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### 🌟 Top 5 Tools")
        if not _display_ratings.empty:
            top_5 = _display_ratings.nlargest(5, "overall_10")[["tool", "overall_10", "n"]]
            st.dataframe(
                top_5.reset_index(drop=True),
                hide_index=True,
                column_config={
                    "tool": "Tool",
                    "overall_10": st.column_config.ProgressColumn("Score", min_value=0, max_value=10),
                    "n": "Mentions"
                },
                use_container_width=True
            )
        else:
            st.info("No data available.")

    with col2:
        st.markdown("##### 📉 Bottom 5 Tools")
        if not _display_ratings.empty:
            bottom_5 = _display_ratings.nsmallest(5, "overall_10")[["tool", "overall_10", "n"]]
            st.dataframe(
                bottom_5.reset_index(drop=True),
                hide_index=True,
                column_config={
                    "tool": "Tool",
                    "overall_10": st.column_config.ProgressColumn("Score", min_value=0, max_value=10),
                    "n": "Mentions"
                },
                use_container_width=True
            )
        else:
            st.info("No data available.")

with _tabs[3]:
    st.markdown("### ⚖️ Compare Tools Side-by-Side")
    st.markdown("*Select two tools to compare their performance metrics*")
    st.markdown("")
    tool_comparison_section(_display_ratings, _filtered_df)

with _tabs[4]:
    st.markdown("### 🔍 Detailed Tool Analysis")
    st.markdown("*In-depth view of individual tool performance and user feedback*")
    st.markdown("")
    details_panel(_display_ratings, _filtered_df)

st.divider()

# Footer
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns([2, 1, 1])
with footer_col1:
    st.markdown("**AISentinel** — Real-time sentiment analysis of AI tools")
    st.caption("Powered by advanced machine learning and natural language processing")
with footer_col2:
    st.markdown("**📊 Data Sources**")
    st.caption("Twitter, Reddit, Hacker News")
with footer_col3:
    st.markdown("**🔄 Updates**")
    st.caption("Refreshed hourly")
