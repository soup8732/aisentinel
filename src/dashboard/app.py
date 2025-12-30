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
from src.utils.logo_service import get_logo_html, get_logo_url_cached

st.set_page_config(
    page_title="AISentinel - AI Tools Reviews",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Vibrant Tech/Fun CSS - Responsive Design System
st.markdown("""
<style>
    /* ============================================
       VIBRANT TECH/FUN COLOR SCHEME
       ============================================ */
    :root {
        /* Primary Colors - Electric Blue/Cyan */
        --primary-cyan: #00d4ff;
        --primary-blue: #0066ff;
        --primary-blue-alt: #3b82f6;
        
        /* Secondary Colors - Vibrant Purple */
        --secondary-purple: #8b5cf6;
        --secondary-purple-alt: #a855f7;
        --secondary-purple-dark: #9333ea;
        
        /* Accent Colors */
        --accent-green: #00ff88;
        --accent-green-alt: #10b981;
        --accent-orange: #ff6b35;
        --accent-orange-alt: #f59e0b;
        
        /* Background Colors */
        --bg-dark: #0f172a;
        --bg-dark-alt: #1e293b;
        --bg-light: #ffffff;
        --bg-light-alt: #f8fafc;
        
        /* Text Colors */
        --text-dark: #0f172a;
        --text-light: #ffffff;
        --text-muted: #64748b;
        
        /* Spacing Scale */
        --spacing-xs: 4px;
        --spacing-sm: 8px;
        --spacing-md: 12px;
        --spacing-lg: 16px;
        --spacing-xl: 24px;
        --spacing-2xl: 32px;
        
        /* Border Radius */
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 20px;
    }
    
    /* ============================================
       GLOBAL STYLES - MOBILE FIRST
       ============================================ */
    .stApp {
        background: linear-gradient(135deg, var(--bg-light-alt) 0%, #e0e7ff 100%);
        background-attachment: fixed;
    }
    
    /* Fluid Typography */
    html {
        font-size: 16px;
        scroll-behavior: smooth;
    }
    
    /* ============================================
       HEADER - COMPACT & VIBRANT
       ============================================ */
    .main-header {
        text-align: center;
        padding: clamp(1.5rem, 4vw, 2rem) clamp(1rem, 3vw, 2rem);
        background: linear-gradient(135deg, var(--primary-cyan) 0%, var(--secondary-purple) 50%, var(--primary-blue) 100%);
        border-radius: var(--radius-lg);
        margin-bottom: clamp(1rem, 3vw, 2rem);
        color: var(--text-light);
        box-shadow: 0 8px 32px rgba(0, 212, 255, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
        animation: pulse 6s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.4; }
        50% { transform: scale(1.1); opacity: 0.7; }
    }
    
    .main-header h1 {
        color: var(--text-light) !important;
        font-size: clamp(2rem, 5vw, 3rem);
        margin-bottom: var(--spacing-sm);
        font-weight: 800;
        text-shadow: 0 2px 8px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
        letter-spacing: -0.02em;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.95);
        font-size: clamp(0.9rem, 2vw, 1.1rem);
        font-weight: 400;
        position: relative;
        z-index: 1;
        margin-bottom: var(--spacing-md);
    }
    
    .main-header .badge-container {
        display: flex;
        justify-content: center;
        gap: var(--spacing-sm);
        flex-wrap: wrap;
        margin-top: var(--spacing-md);
        position: relative;
        z-index: 1;
    }
    
    .main-header .badge {
        background: rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
        padding: var(--spacing-sm) var(--spacing-lg);
        border-radius: 20px;
        font-size: clamp(0.75rem, 1.5vw, 0.85rem);
        border: 1px solid rgba(255,255,255,0.3);
    }
    
    .github-link {
        position: absolute;
        top: clamp(0.75rem, 2vw, 1rem);
        right: clamp(1rem, 3vw, 1.5rem);
        color: var(--text-light);
        text-decoration: none;
        font-size: 1.25rem;
        opacity: 0.9;
        transition: all 0.3s ease;
        z-index: 2;
        background: rgba(255,255,255,0.2);
        padding: var(--spacing-sm);
        border-radius: 50%;
        backdrop-filter: blur(10px);
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .github-link:hover {
        opacity: 1;
        transform: scale(1.1) rotate(5deg);
        background: rgba(255,255,255,0.3);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    /* ============================================
       METRICS - VIBRANT STYLING
       ============================================ */
    [data-testid="stMetricValue"] {
        font-size: clamp(1.5rem, 4vw, 2rem);
        font-weight: 700;
        background: linear-gradient(135deg, var(--primary-cyan) 0%, var(--secondary-purple) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    [data-testid="stMetricLabel"] {
        font-weight: 600;
        color: var(--text-muted);
        font-size: clamp(0.85rem, 2vw, 0.95rem);
    }
    
    /* ============================================
       CONTAINER & SPACING
       ============================================ */
    .block-container {
        padding: clamp(1rem, 3vw, 2rem) clamp(1rem, 4vw, 2rem);
        max-width: 1400px;
        margin: 0 auto;
    }
    
    .element-container {
        margin-bottom: var(--spacing-md);
    }
    
    [data-testid="stMarkdownContainer"] {
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Better text rendering */
    body {
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        text-rendering: optimizeLegibility;
    }
    
    /* Fix line heights globally */
    p, div, span {
        line-height: 1.5 !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        line-height: 1.3 !important;
        margin: 0.5em 0 !important;
    }
    
    /* ============================================
       CARDS - CLEAN PROFESSIONAL STYLE (NO BLACK BORDERS!)
       ============================================ */
    
    /* Card styling - target the column's vertical block which contains the card container */
    /* Primary target: cards inside columns - use more specific selectors */
    [data-testid="column"] > div[data-testid="stVerticalBlock"],
    [data-testid="column"] > [data-testid="stVerticalBlock"],
    div[data-testid="column"] > div[data-testid="stVerticalBlock"],
    [data-testid="column"] > div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%) !important;
        border-radius: 16px !important;
        padding: 16px !important;
        border: 2px solid rgba(0, 212, 255, 0.4) !important;
        box-shadow: 0 6px 24px rgba(0, 212, 255, 0.2), 0 2px 8px rgba(139, 92, 246, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.8) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        margin-bottom: 16px !important;
        position: relative !important;
        overflow: visible !important;
    }
    
    /* Top accent bar for cards */
    [data-testid="column"] > div[data-testid="stVerticalBlock"]::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 3px !important;
        background: linear-gradient(90deg, #00d4ff 0%, #8b5cf6 50%, #0066ff 100%) !important;
        border-radius: 16px 16px 0 0 !important;
        z-index: 1 !important;
    }
    
    /* Card hover effect */
    [data-testid="column"] > div[data-testid="stVerticalBlock"]:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 32px rgba(0, 212, 255, 0.3), 0 4px 12px rgba(139, 92, 246, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.9) !important;
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%) !important;
        border-color: rgba(0, 212, 255, 0.6) !important;
    }
    
    /* Fallback: target nested vertical blocks */
    [data-testid="column"] > [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%) !important;
        border-radius: 16px !important;
        padding: 16px !important;
        border: 2px solid rgba(0, 212, 255, 0.4) !important;
        box-shadow: 0 6px 24px rgba(0, 212, 255, 0.2), 0 2px 8px rgba(139, 92, 246, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.8) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        margin-bottom: 16px !important;
        position: relative !important;
        overflow: visible !important;
    }
    
    [data-testid="column"] > [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"]::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 3px !important;
        background: linear-gradient(90deg, #00d4ff 0%, #8b5cf6 50%, #0066ff 100%) !important;
        border-radius: 16px 16px 0 0 !important;
        z-index: 1 !important;
    }
    
    [data-testid="column"] > [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"]:hover,
    div[data-testid="column"] > div[data-testid="stVerticalBlock"]:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 32px rgba(0, 212, 255, 0.3), 0 4px 12px rgba(139, 92, 246, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.9) !important;
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%) !important;
        border-color: rgba(0, 212, 255, 0.6) !important;
    }
    
    /* Ensure logo images are visible */
    [data-testid="column"] img[id^="logo-"],
    [data-testid="column"] div[id^="logo-"],
    [data-testid="column"] img,
    [data-testid="column"] .logo-fallback {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
    }
    
    /* Logo container styling */
    [data-testid="column"] div[id^="logo-"] {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Ensure logo images load properly */
    [data-testid="column"] img {
        max-width: 100% !important;
        height: auto !important;
    }
    
    /* Reduce spacing in card containers */
    [data-testid="column"] > div[data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"],
    [data-testid="column"] > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] {
        margin-bottom: 8px !important;
    }
    
    [data-testid="column"] > div[data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:last-child {
        margin-bottom: 0 !important;
    }
    
    /* Text styling in cards */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] h3 {
        margin: 0 0 6px 0 !important;
        padding: 0 !important;
        line-height: 1.3 !important;
        color: #0f172a !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] p {
        margin: 6px 0 !important;
        line-height: 1.5 !important;
    }
    
    /* Fix markdown container spacing */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] [data-testid="stMarkdownContainer"] {
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Column spacing in cards */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] [data-testid="column"] {
        padding: 0 8px !important;
    }
    
    /* Remove ALL borders from containers and cards */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] > div[data-baseweb="card"],
    [data-baseweb="card"],
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
        border: none !important;
    }
    
    /* Remove borders from Streamlit containers */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
        border: none !important;
        outline: none !important;
    }
    
    /* Logo container styling */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] .logo-container,
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] [data-testid="stMarkdownContainer"]:has(div[id^="logo-"]) {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Divider styling in cards */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] hr {
        margin: 16px 0 !important;
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.2), transparent) !important;
    }
    
    /* Button container spacing */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] .stButton {
        margin-top: 4px !important;
        margin-bottom: 0 !important;
    }
    
    /* Logo display improvements */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] img[id^="logo-"] {
        border-radius: 12px;
        object-fit: contain;
    }
    
    /* Score badge improvements */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] [data-testid="stMarkdownContainer"]:has(div[style*="text-align: center"][style*="background:"]) {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Category badge styling */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] span[style*="background: linear-gradient"] {
        margin-top: 4px !important;
        display: inline-block !important;
    }
    
    /* Better spacing between card sections */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] {
        margin-bottom: 12px !important;
    }
    
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:last-of-type {
        margin-bottom: 0 !important;
    }
    
    /* ============================================
       BUTTONS - VIBRANT GRADIENTS
       ============================================ */
    .stButton>button {
        border-radius: var(--radius-md);
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        background: linear-gradient(135deg, var(--primary-cyan) 0%, var(--secondary-purple) 100%);
        border: none;
        color: var(--text-light);
        padding: var(--spacing-md) var(--spacing-xl);
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3);
        min-height: 44px; /* Touch-friendly */
        font-size: clamp(0.9rem, 2vw, 1rem);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(139, 92, 246, 0.4);
        background: linear-gradient(135deg, var(--secondary-purple) 0%, var(--primary-blue) 100%);
    }
    
    .stButton>button:active {
        transform: translateY(0);
    }
    
    .stButton>button[kind="secondary"] {
        background: var(--bg-light);
        color: var(--primary-blue);
        border: 2px solid var(--primary-cyan);
        box-shadow: 0 2px 8px rgba(0, 212, 255, 0.2);
    }
    
    .stButton>button[kind="secondary"]:hover {
        background: linear-gradient(135deg, var(--primary-cyan) 0%, var(--secondary-purple) 100%);
        color: var(--text-light);
        border-color: transparent;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3);
    }
    
    /* ============================================
       TABS - VIBRANT STYLING
       ============================================ */
    .stTabs [data-baseweb="tab-list"] {
        gap: var(--spacing-sm);
        background: rgba(255, 255, 255, 0.9);
        padding: var(--spacing-sm);
        border-radius: var(--radius-md);
        backdrop-filter: blur(10px);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: var(--radius-md);
        padding: var(--spacing-md) var(--spacing-xl);
        font-weight: 600;
        transition: all 0.3s ease;
        background: transparent;
        font-size: clamp(0.85rem, 2vw, 0.95rem);
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary-cyan) 0%, var(--secondary-purple) 100%);
        color: var(--text-light);
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(0, 212, 255, 0.1);
    }
    
    /* ============================================
       INPUTS & SELECTS - CLEAN FILTER STYLING
       ============================================ */
    .stSelectbox, .stMultiSelect, .stTextInput {
        background: var(--bg-light);
        border-radius: var(--radius-md);
    }
    
    .stSelectbox > div > div {
        border-radius: var(--radius-md);
        border: 2px solid rgba(0, 212, 255, 0.15);
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:hover {
        border-color: var(--primary-cyan);
        box-shadow: 0 2px 8px rgba(0, 212, 255, 0.15);
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: var(--primary-cyan);
        box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.1);
    }
    
    .stTextInput > div > div > input {
        border-radius: var(--radius-md);
        border: 2px solid rgba(0, 212, 255, 0.15);
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--primary-cyan);
        box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.1);
    }
    
    .stMultiSelect > div {
        border-radius: var(--radius-md);
        border: 2px solid rgba(0, 212, 255, 0.15);
        transition: all 0.3s ease;
    }
    
    .stMultiSelect > div:hover {
        border-color: var(--primary-cyan);
        box-shadow: 0 2px 8px rgba(0, 212, 255, 0.15);
    }
    
    .stSelectbox label, .stMultiSelect label, .stTextInput label, .stRadio label {
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: unset !important;
        font-weight: 600;
        color: var(--text-dark);
        font-size: clamp(0.85rem, 2vw, 0.95rem);
        margin-bottom: 6px !important;
    }
    
    /* Radio button styling for view mode */
    .stRadio > div {
        gap: 12px;
    }
    
    .stRadio > div > label {
        padding: 8px 16px;
        border-radius: var(--radius-md);
        border: 2px solid rgba(0, 212, 255, 0.2);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .stRadio > div > label:hover {
        border-color: var(--primary-cyan);
        background: rgba(0, 212, 255, 0.05);
    }
    
    .stRadio > div > label[data-testid="stRadio"] {
        background: linear-gradient(135deg, var(--primary-cyan) 0%, var(--secondary-purple) 100%);
        color: white;
        border-color: transparent;
    }
    
    /* Expander styling for date filter */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: var(--text-dark);
        padding: 12px 0;
    }
    
    .streamlit-expanderHeader:hover {
        color: var(--primary-blue);
    }
    
    /* Date input styling */
    .stDateInput > div > div > input {
        border-radius: var(--radius-md);
        border: 2px solid rgba(0, 212, 255, 0.15);
    }
    
    .stDateInput > div > div > input:focus {
        border-color: var(--primary-cyan);
        box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.1);
    }
    
    /* Better spacing for filter sections */
    [data-testid="stSidebar"] .element-container {
        margin-bottom: 20px !important;
    }
    
    [data-testid="stSidebar"] .element-container:last-child {
        margin-bottom: 0 !important;
    }
    
    [data-testid="stSidebar"] hr {
        margin: 20px 0 !important;
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.2), transparent) !important;
    }
    
    /* Sidebar section headings */
    [data-testid="stSidebar"] h3 {
        margin-top: 0 !important;
        margin-bottom: 20px !important;
        font-size: 1.25rem !important;
        color: var(--text-dark) !important;
        font-weight: 700 !important;
    }
    
    /* Remove excessive spacing from markdown in sidebar */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        margin-bottom: 0 !important;
    }
    
    /* Better spacing for success messages */
    [data-testid="stSidebar"] .stSuccess {
        margin-top: 12px !important;
        margin-bottom: 16px !important;
        padding: 12px !important;
    }
    
    /* Consistent spacing for all sidebar inputs */
    [data-testid="stSidebar"] .stSelectbox,
    [data-testid="stSidebar"] .stTextInput,
    [data-testid="stSidebar"] .stMultiSelect {
        margin-bottom: 0 !important;
    }
    
    /* Remove extra spacing from columns in sidebar */
    [data-testid="stSidebar"] [data-testid="column"] {
        padding: 0 4px !important;
    }
    
    /* ============================================
       SIDEBAR - RESPONSIVE
       ============================================ */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-right: 2px solid rgba(0, 212, 255, 0.1);
    }
    
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        background: transparent;
    }
    
    /* Sidebar content styling */
    [data-testid="stSidebar"] .stMarkdown {
        font-size: clamp(0.85rem, 2vw, 0.95rem);
    }
    
    [data-testid="stSidebar"] .stSelectbox,
    [data-testid="stSidebar"] .stMultiSelect,
    [data-testid="stSidebar"] .stTextInput {
        font-size: clamp(0.85rem, 2vw, 0.95rem);
    }
    
    /* Mobile sidebar adjustments */
    @media (max-width: 767px) {
        [data-testid="stSidebar"] {
            width: 100% !important;
            max-width: 100% !important;
        }
        
        /* Hide sidebar by default on mobile, show on toggle */
        [data-testid="stSidebar"][aria-expanded="false"] {
            transform: translateX(-100%);
            transition: transform 0.3s ease;
        }
        
        [data-testid="stSidebar"][aria-expanded="true"] {
            transform: translateX(0);
            transition: transform 0.3s ease;
        }
    }
    
    /* ============================================
       PROGRESS BARS
       ============================================ */
    [data-testid="stProgress"] > div > div {
        background: linear-gradient(90deg, var(--primary-cyan) 0%, var(--secondary-purple) 100%);
        border-radius: var(--radius-md);
    }
    
    /* ============================================
       DATA TABLES
       ============================================ */
    .dataframe {
        border-radius: var(--radius-md);
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* ============================================
       MESSAGES
       ============================================ */
    .stSuccess {
        background: linear-gradient(135deg, rgba(0, 255, 136, 0.1) 0%, rgba(16, 185, 129, 0.1) 100%);
        border-left: 4px solid var(--accent-green);
        border-radius: var(--radius-sm);
        padding: var(--spacing-lg);
    }
    
    .stInfo {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%);
        border-left: 4px solid var(--primary-cyan);
        border-radius: var(--radius-sm);
        padding: var(--spacing-lg);
    }
    
    .stWarning {
        background: linear-gradient(135deg, rgba(255, 107, 53, 0.1) 0%, rgba(245, 158, 11, 0.1) 100%);
        border-left: 4px solid var(--accent-orange);
        border-radius: var(--radius-sm);
        padding: var(--spacing-lg);
    }
    
    /* ============================================
       DIVIDERS
       ============================================ */
    hr {
        margin: var(--spacing-xl) 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--primary-cyan), transparent);
        opacity: 0.4;
    }
    
    /* ============================================
       EXPANDERS
       ============================================ */
    .streamlit-expanderHeader {
        font-weight: 600;
        border-radius: var(--radius-md);
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(0, 212, 255, 0.1);
    }
    
    /* ============================================
       RESPONSIVE DESIGN - MOBILE FIRST
       ============================================ */
    
    /* Mobile: < 768px */
    @media (max-width: 767px) {
        .block-container {
            padding: var(--spacing-lg) var(--spacing-md);
        }
        
        .main-header {
            padding: var(--spacing-xl) var(--spacing-md);
        }
        
        .main-header h1 {
            font-size: clamp(1.75rem, 6vw, 2.25rem);
        }
        
        /* Force single column on mobile for card grid */
        [data-testid="stHorizontalBlock"][data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
        }
        
        /* Ensure cards stack on mobile */
        [data-testid="column"] {
            min-width: 100% !important;
            flex: 1 1 100% !important;
            max-width: 100% !important;
        }
        
        /* Sidebar adjustments */
        [data-testid="stSidebar"] {
            width: 100% !important;
        }
        
        /* Smaller score badges on mobile */
        .score-badge {
            padding: var(--spacing-md) var(--spacing-sm) !important;
        }
    }
    
    /* Tablet: 768px - 1024px */
    @media (min-width: 768px) and (max-width: 1024px) {
        .block-container {
            padding: var(--spacing-xl) var(--spacing-lg);
        }
        
        /* 2 columns on tablet for card grid - Streamlit handles this automatically */
    }
    
    /* Desktop: > 1024px */
    @media (min-width: 1025px) {
        .block-container {
            padding: var(--spacing-2xl) var(--spacing-xl);
        }
        
        /* 3 columns on desktop for card grid - Streamlit handles this automatically */
    }
    
    /* ============================================
       LINK BUTTONS - Consistent styling with regular buttons
       ============================================ */
    a.stLinkButton,
    a.stLinkButton > button {
        border-radius: var(--radius-md) !important;
        font-weight: 600 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        background: var(--bg-light) !important;
        color: var(--primary-blue) !important;
        border: 2px solid var(--primary-cyan) !important;
        box-shadow: 0 2px 8px rgba(0, 212, 255, 0.2) !important;
        padding: var(--spacing-md) var(--spacing-xl) !important;
        min-height: 44px !important;
        font-size: clamp(0.9rem, 2vw, 1rem) !important;
        text-decoration: none !important;
        display: inline-block !important;
        width: 100% !important;
        text-align: center !important;
    }
    
    a.stLinkButton:hover,
    a.stLinkButton > button:hover {
        transform: translateY(-2px) !important;
        background: linear-gradient(135deg, var(--primary-cyan) 0%, var(--secondary-purple) 100%) !important;
        color: var(--text-light) !important;
        border-color: transparent !important;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3) !important;
    }
    
    a.stLinkButton:active,
    a.stLinkButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* ============================================
       UTILITY CLASSES
       ============================================ */
    .logo-container {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        margin-bottom: 0;
        padding: 0;
    }
    
    .score-badge {
        text-align: center;
        padding: var(--spacing-lg) var(--spacing-md);
        border-radius: var(--radius-md);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        transition: all 0.3s ease;
        margin: 0;
    }
    
    .score-badge:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
    }
    
    /* Image styling in cards */
    [data-testid="stImage"] {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    [data-testid="stImage"] img {
        border-radius: 12px !important;
        object-fit: contain !important;
        background: rgba(0, 212, 255, 0.05) !important;
        padding: 8px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Better divider spacing */
    hr {
        margin: 16px 0 !important;
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.3), transparent) !important;
    }
    
    /* Fix container padding issues */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] > div {
        padding: 0 !important;
    }
    
    /* Better spacing between elements in cards */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] {
        margin-bottom: 12px !important;
    }
    
    /* Fix button spacing */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] .stButton {
        margin-top: 8px !important;
        margin-bottom: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Compact vibrant header
st.markdown("""
<div class="main-header">
    <a href="https://github.com/soup8732/aisentinel" target="_blank" class="github-link" title="View on GitHub">
        <svg height="20" width="20" viewBox="0 0 16 16" fill="currentColor">
            <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
        </svg>
    </a>
    <h1>🤖 AISentinel</h1>
    <p>Real-time sentiment analysis of AI tools based on user feedback</p>
    <div class="badge-container">
        <span class="badge">📊 Live Analytics</span>
        <span class="badge">🔬 Technical Metrics</span>
        <span class="badge">💭 User Sentiment</span>
    </div>
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

# Official website links for all tracked AI tools
# All links verified to official websites (as of 2024)
# Every tool in src/utils/taxonomy.py has a corresponding entry here
# Links are displayed in tool cards, detail modals, and detail panels
TOOL_LINKS: Dict[str, str] = {
    # Text & Chat Models
    "ChatGPT": "https://chat.openai.com/",
    "Claude": "https://claude.ai/",
    "Gemini": "https://gemini.google.com/",
    "DeepSeek": "https://www.deepseek.com/",
    "Mistral": "https://mistral.ai/",
    "Jasper": "https://www.jasper.ai/",
    "Copy.ai": "https://www.copy.ai/",
    "Writesonic": "https://writesonic.com/",
    "Lindy": "https://www.lindy.ai/",
    
    # Coding & Dev Tools
    "GitHub Copilot": "https://github.com/features/copilot",
    "Amazon Q Developer": "https://aws.amazon.com/q/developer/",
    "CodeWhisperer": "https://aws.amazon.com/codewhisperer/",
    "Tabnine": "https://www.tabnine.com/",
    "Tabby": "https://tabby.tabbyml.com/",
    "Replit Ghostwriter": "https://replit.com/site/ghostwriter",
    "Bolt": "https://bolt.new/",
    "Loveable": "https://www.lovable.dev/",
    "JetBrains AI Assistant": "https://www.jetbrains.com/ai/",
    "Cursor": "https://cursor.sh/",
    "Codeium": "https://codeium.com/",
    "Polycoder": "https://huggingface.co/NinedayWang/PolyCoder-2.7B",
    "AskCodi": "https://www.askcodi.com/",
    "Sourcery": "https://sourcery.ai/",
    "Greta": "https://greta.ai/",
    
    # Image & Video Tools
    "Stability AI": "https://stability.ai/",
    "RunwayML": "https://runwayml.com/",
    "Midjourney": "https://www.midjourney.com/",
    "DALL-E": "https://openai.com/dall-e-3",
    "DreamStudio": "https://dreamstudio.ai/",
    "OpenCV": "https://opencv.org/",
    "Adobe Firefly": "https://www.adobe.com/sensei/generative-ai/firefly.html",
    "Pika Labs": "https://pika.art/",
    "Luma Dream Machine": "https://lumalabs.ai/dream-machine",
    "Vidu": "https://www.vidu.ai/",
    
    # Audio & Speech Tools
    "Whisper": "https://openai.com/research/whisper",
    "ElevenLabs": "https://elevenlabs.io/",
    "Murf AI": "https://murf.ai/",
    "PlayHT": "https://play.ht/",
    "Speechify": "https://speechify.com/",
    "Synthesys": "https://www.synthesys.io/",
    "Animaker": "https://www.animaker.com/",
    "Kits AI": "https://www.kits.ai/",
    "WellSaid Labs": "https://wellsaidlabs.com/",
    "Hume": "https://www.hume.ai/",
    "DupDub": "https://www.dupdub.com/",
}

def get_company_name_for_tool(tool_name: str) -> Optional[str]:
    """Get the ArtificialAnalysis creator name for a tool.
    
    This function maps tool names to creator names that match the API's model_creator.name field.
    It also handles common variations and fuzzy matching.
    
    Args:
        tool_name: Name of the tool from taxonomy
        
    Returns:
        Creator name for API lookup, or None if not found
    """
    # Direct mapping
    direct_mapping = TOOL_TO_COMPANY.get(tool_name)
    if direct_mapping:
        return direct_mapping
    
    # Try fuzzy matching for common variations
    tool_lower = tool_name.lower()
    
    # Common creator name variations
    if "openai" in tool_lower or tool_name in ["ChatGPT", "DALL-E", "Whisper"]:
        return "OpenAI"
    if "anthropic" in tool_lower or "claude" in tool_lower:
        return "Anthropic"
    if "google" in tool_lower or "gemini" in tool_lower:
        return "Google"
    if "amazon" in tool_lower or "aws" in tool_lower:
        return "Amazon"
    if "github" in tool_lower or "copilot" in tool_lower:
        return "GitHub"
    if "mistral" in tool_lower:
        return "Mistral AI"
    if "deepseek" in tool_lower:
        return "DeepSeek"
    if "stability" in tool_lower:
        return "Stability AI"
    if "midjourney" in tool_lower:
        return "Midjourney"
    if "runway" in tool_lower:
        return "Runway"
    if "adobe" in tool_lower:
        return "Adobe"
    if "elevenlabs" in tool_lower:
        return "ElevenLabs"
    if "tabnine" in tool_lower:
        return "Tabnine"
    if "cursor" in tool_lower:
        return "Cursor"
    if "codeium" in tool_lower:
        return "Codeium"
    if "replit" in tool_lower:
        return "Replit"
    if "jetbrains" in tool_lower:
        return "JetBrains"
    
    return None


# Mapping from tool names to ArtificialAnalysis company/creator names
# These map to the model_creator.name field in the API response
TOOL_TO_COMPANY: Dict[str, str] = {
    # Text & Chat Models
    "ChatGPT": "OpenAI",
    "Claude": "Anthropic",
    "Gemini": "Google",
    "DeepSeek": "DeepSeek",
    "Mistral": "Mistral AI",
    "Jasper": "Jasper",  # May need to verify actual creator name
    "Copy.ai": "Copy.ai",  # May need to verify
    "Writesonic": "Writesonic",  # May need to verify
    "Lindy": "Lindy",  # May need to verify
    
    # Coding & Dev Tools
    "GitHub Copilot": "GitHub",
    "Amazon Q Developer": "Amazon",
    "CodeWhisperer": "Amazon",
    "Tabnine": "Tabnine",
    "Tabby": "Tabby",  # May need to verify
    "Replit Ghostwriter": "Replit",
    "Bolt": "Bolt",  # May need to verify
    "Loveable": "Loveable",  # May need to verify
    "JetBrains AI Assistant": "JetBrains",
    "Cursor": "Cursor",
    "Codeium": "Codeium",
    "Polycoder": "Polycoder",  # May need to verify
    "AskCodi": "AskCodi",  # May need to verify
    "Sourcery": "Sourcery",  # May need to verify
    "Greta": "Greta",  # May need to verify
    
    # Image & Video Tools
    "Stability AI": "Stability AI",
    "RunwayML": "Runway",
    "Midjourney": "Midjourney",
    "DALL-E": "OpenAI",
    "DreamStudio": "Stability AI",  # Part of Stability AI
    "OpenCV": "OpenCV",  # May not be in API
    "Adobe Firefly": "Adobe",
    "Pika Labs": "Pika Labs",  # May need to verify
    "Luma Dream Machine": "Luma AI",  # May need to verify
    "Vidu": "Vidu",  # May need to verify
    
    # Audio & Speech Tools
    "Whisper": "OpenAI",
    "ElevenLabs": "ElevenLabs",
    "Murf AI": "Murf AI",  # May need to verify
    "PlayHT": "PlayHT",  # May need to verify
    "Speechify": "Speechify",  # May need to verify
    "Synthesys": "Synthesys",  # May need to verify
    "Animaker": "Animaker",  # May need to verify
    "Kits AI": "Kits AI",  # May need to verify
    "WellSaid Labs": "WellSaid Labs",  # May need to verify
    "Hume": "Hume AI",  # May need to verify
    "DupDub": "DupDub",  # May need to verify
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
    # Clean, organized filter layout with proper spacing
    st.markdown("### 🔍 Filters")
    
    # Quick jump to tool - clean and prominent
    all_tools = sorted(df_ratings["tool"].unique().tolist())
    selected_tool = st.selectbox(
        "Quick Jump to Tool",
        [""] + all_tools,
        placeholder="Search for a tool...",
        key="quick_search",
        help="Quickly navigate to a specific tool's details"
    )
    if selected_tool:
        st.session_state["selected_tool"] = selected_tool
        st.session_state["goto_details"] = True
        st.success(f"✨ **{selected_tool}** selected! Switch to 'Details' tab to view.")
    
    # Search filter
    query = st.text_input(
        "Search by Name",
        placeholder="Enter tool name...",
        help="Filter tools by name (case-insensitive)",
        key="search_query"
    )
    
    # Category filter
    raw_cats = sorted(df_ratings["category"].astype(str).unique().tolist())
    friendly_list = sorted({FRIENDLY_LABEL.get(c, c.replace('_',' ').title()) for c in raw_cats})
    label_to_raw: Dict[str, List[str]] = {}
    for rc in raw_cats:
        lbl = FRIENDLY_LABEL.get(rc, rc.replace('_',' ').title())
        label_to_raw.setdefault(lbl, []).append(rc)
    
    sel_labels = st.multiselect(
        "Categories",
        friendly_list,
        default=friendly_list,
        help="Select categories to filter",
        key="category_filter"
    )
    selected_raw = [rc for lbl in sel_labels for rc in label_to_raw.get(lbl, [])]
    
    # Display options - side by side
    display_col1, display_col2 = st.columns(2)
    
    with display_col1:
        top_n = int(st.selectbox(
            "Show Top",
            [5, 10, 20, 50],
            index=1,
            help="Number of top tools to display",
            key="top_n_filter"
        ))
    
    with display_col2:
        view_mode = st.radio(
            "View Mode",
            ["Cards", "Table"],
            horizontal=True,
            help="Switch between card and table view",
            key="view_mode_filter"
        )
    
    # Date filtering in collapsible section - cleaner design
    date_range = None
    if not df_raw.empty and "created_at" in df_raw.columns:
        with st.expander("📅 Date Range Filter", expanded=False):
            min_date = df_raw["created_at"].min().date()
            max_date = df_raw["created_at"].max().date()
            
            # Get preset dates if buttons were clicked
            preset_start = st.session_state.get("preset_start")
            preset_end = st.session_state.get("preset_end")
            
            default_start = preset_start if preset_start and preset_start >= min_date else min_date
            default_end = preset_end if preset_end and preset_end <= max_date else max_date
            
            col_date1, col_date2 = st.columns(2)
            with col_date1:
                start_date = st.date_input(
                    "From",
                    value=default_start,
                    min_value=min_date,
                    max_value=max_date,
                    help="Start date for filtering",
                    key="date_start"
                )
            with col_date2:
                end_date = st.date_input(
                    "To",
                    value=default_end,
                    min_value=min_date,
                    max_value=max_date,
                    help="End date for filtering",
                    key="date_end"
                )
            
            if start_date and end_date:
                start_ts = pd.Timestamp(start_date).tz_localize('UTC')
                end_ts = pd.Timestamp(end_date).tz_localize('UTC')
                date_range = (start_ts, end_ts)
            
            # Quick date presets
            st.markdown("**Quick Presets:**")
            preset_col1, preset_col2, preset_col3 = st.columns(3)
            with preset_col1:
                if st.button("Last 7 Days", use_container_width=True, key="preset_7d"):
                    end = max_date
                    start = (pd.Timestamp(end) - pd.Timedelta(days=7)).date()
                    if start < min_date:
                        start = min_date
                    st.session_state["preset_start"] = start
                    st.session_state["preset_end"] = end
                    st.rerun()
            with preset_col2:
                if st.button("Last 30 Days", use_container_width=True, key="preset_30d"):
                    end = max_date
                    start = (pd.Timestamp(end) - pd.Timedelta(days=30)).date()
                    if start < min_date:
                        start = min_date
                    st.session_state["preset_start"] = start
                    st.session_state["preset_end"] = end
                    st.rerun()
            with preset_col3:
                if st.button("All Time", use_container_width=True, key="preset_all"):
                    st.session_state["preset_start"] = min_date
                    st.session_state["preset_end"] = max_date
                    st.rerun()

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
    
    # Get company name for API lookup (with fuzzy matching)
    company_name = get_company_name_for_tool(tool_name)
    
    if company_name:
        try:
            # Initialize API client
            api_client = ArtificialAnalysisClient()
            
            # Cache key for this company's models
            cache_key = f"aa_models_{company_name}"
            
            # Fetch models from this company (with caching)
            if cache_key not in st.session_state:
                with st.spinner(f"Loading models from {company_name}..."):
                    company_models = api_client.get_models_by_creator(company_name)
                    st.session_state[cache_key] = company_models
            else:
                company_models = st.session_state[cache_key]
            
            if company_models:
                # Model selection dropdown - use session state to persist selection
                model_session_key = f"selected_model_{tool_name}"
                
                # Create model options with better display names
                model_options = {}
                for m in company_models:
                    display_name = f"{m.name}"
                    if m.slug and m.slug != m.name.lower().replace(" ", "-"):
                        display_name += f" ({m.slug})"
                    model_options[display_name] = m
                
                model_names = list(model_options.keys())
                
                if model_names:
                    # Get previously selected model or default to first
                    default_idx = 0
                    if model_session_key in st.session_state:
                        prev_selection = st.session_state[model_session_key]
                        if prev_selection in model_names:
                            default_idx = model_names.index(prev_selection)
                    
                    selected_model_key = st.selectbox(
                        f"Select a model from {company_name}",
                        model_names,
                        index=default_idx,
                        key=f"model_select_{tool_name}",
                        help="Choose a specific model to view detailed technical metrics"
                    )
                    
                    # Store selection in session state
                    st.session_state[model_session_key] = selected_model_key
                    
                    selected_model: ModelInfo = model_options[selected_model_key]
                    
                    # Display technical metrics
                    st.markdown(f"#### 📊 {selected_model.name} Technical Specifications")
                    
                    # Three-column layout for better organization
                    tech_col1, tech_col2, tech_col3 = st.columns(3)
                    
                    # COLUMN 1: All Evaluation Scores
                    with tech_col1:
                        st.markdown("**📈 Evaluation Scores**")
                        if selected_model.evaluations:
                            eval_data = selected_model.evaluations
                            
                            # Display ALL evaluation metrics
                            for key, value in sorted(eval_data.items()):
                                if isinstance(value, (int, float)):
                                    # Format label nicely
                                    label = key.replace("_", " ").title()
                                    
                                    # Determine format based on key
                                    if key.endswith("_index"):
                                        # Index scores (typically 0-100 scale)
                                        formatted_value = f"{value:.1f}"
                                    elif key in ["mmlu_pro", "gpqa", "hle", "livecodebench", "scicode", "math_500", "aime"]:
                                        # Ratio scores (0-1 scale) - show as percentage
                                        formatted_value = f"{value:.1%}"
                                    else:
                                        # Default to 3 decimal places
                                        formatted_value = f"{value:.3f}"
                                    
                                    st.metric(label, formatted_value, help=f"API key: {key}")
                        else:
                            st.info("No evaluation scores available")
                    
                    # COLUMN 2: Pricing Information
                    with tech_col2:
                        st.markdown("**💰 Pricing (per 1M tokens)**")
                        if selected_model.pricing:
                            pricing = selected_model.pricing
                            
                            if "price_1m_input_tokens" in pricing:
                                st.metric(
                                    "Input Tokens",
                                    f"${pricing['price_1m_input_tokens']:.4f}",
                                    help="Price per million input tokens"
                                )
                            if "price_1m_output_tokens" in pricing:
                                st.metric(
                                    "Output Tokens",
                                    f"${pricing['price_1m_output_tokens']:.4f}",
                                    help="Price per million output tokens"
                                )
                            if "price_1m_blended_3_to_1" in pricing:
                                st.metric(
                                    "Blended (3:1)",
                                    f"${pricing['price_1m_blended_3_to_1']:.4f}",
                                    help="Blended pricing (3 input : 1 output ratio)"
                                )
                        else:
                            st.info("No pricing information available")
                    
                    # COLUMN 3: Performance Metrics
                    with tech_col3:
                        st.markdown("**⚡ Performance**")
                        has_perf = False
                        
                        if selected_model.median_output_tokens_per_second is not None:
                            st.metric(
                                "Output Speed",
                                f"{selected_model.median_output_tokens_per_second:.1f} tokens/sec",
                                help="Median output generation speed"
                            )
                            has_perf = True
                        
                        if selected_model.median_time_to_first_token_seconds is not None:
                            st.metric(
                                "Time to First Token",
                                f"{selected_model.median_time_to_first_token_seconds:.2f}s",
                                help="Median time to first token"
                            )
                            has_perf = True
                        
                        if not has_perf:
                            st.info("No performance metrics available")
                    
                    # Model metadata
                    st.markdown("---")
                    st.markdown("**📋 Model Information**")
                    meta_col1, meta_col2 = st.columns(2)
                    with meta_col1:
                        st.caption(f"**Model ID:** `{selected_model.id}`")
                        if selected_model.slug:
                            st.caption(f"**Slug:** `{selected_model.slug}`")
                    with meta_col2:
                        if selected_model.model_creator:
                            creator = selected_model.model_creator
                            st.caption(f"**Creator:** {creator.get('name', 'N/A')}")
                            if creator.get('id'):
                                st.caption(f"**Creator ID:** `{creator['id']}`")
                
                else:
                    st.info(f"Found models from {company_name}, but no models available to display.")
            else:
                st.info(f"No models found for {company_name} in ArtificialAnalysis database. The company may use different naming or may not be tracked yet.")
        
        except ValueError as e:
            # API key not configured
            st.warning("⚠️ **API Key Not Configured**")
            st.info(f"To view technical metrics, add your `AA_API_KEY` as an environment variable or secret file in Render. Visit https://artificialanalysis.ai/ to get an API key.")
            
            # Debug info to help diagnose the issue
            with st.expander("🔍 Debug Information", expanded=False):
                from pathlib import Path
                
                env_check = 'AA_API_KEY' in os.environ
                env_value = os.environ.get('AA_API_KEY')
                secret_file = Path("/etc/secrets/AA_API_KEY")
                secret_exists = secret_file.exists()
                secret_content = None
                
                if secret_exists:
                    try:
                        secret_content = secret_file.read_text().strip()
                        secret_readable = "Yes" if secret_content else "Empty file"
                    except Exception as ex:
                        secret_readable = f"Error reading: {str(ex)}"
                else:
                    secret_readable = "File does not exist"
                
                st.code(f"""
Environment Variable Check:
- AA_API_KEY in os.environ: {env_check}
- AA_API_KEY value: {'Set (length: ' + str(len(env_value)) + ')' if env_value else 'Not set'}

Render Secret File Check:
- /etc/secrets/AA_API_KEY exists: {secret_exists}
- Secret file readable: {secret_readable}
- Secret file content length: {len(secret_content) if secret_content else 0}

All Environment Variables (AA_*):
{chr(10).join([f"- {k}: {'Set' if os.environ.get(k) else 'Not set'}" for k in os.environ.keys() if k.startswith('AA_')]) or '- No AA_* variables found'}

Error: {str(e)}
                """)
            
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
    tool_name = str(row["tool"])
    category_label = row.get("type_label", "")

    # Score gradient helper - using vibrant tech colors
    def get_score_gradient(score):
        if score >= 7:
            return "linear-gradient(135deg, #00ff88 0%, #10b981 100%)"
        elif score >= 5:
            return "linear-gradient(135deg, #ff6b35 0%, #f59e0b 100%)"
        else:
            return "linear-gradient(135deg, #ef4444 0%, #dc2626 100%)"

    # Get scores
    overall_score = int(row["overall_10"])
    perception_score = int(row["perception_10"])
    privacy_score = int(row["privacy_10"])

    # Always use HTML for logo (never st.image for external URLs)
    fallback_text = tool_name[:2].upper()
    logo_html = get_logo_html(tool_name, size=60, fallback_text=fallback_text)

    # Get website URL
    url = TOOL_LINKS.get(tool_name)
    
    # Card container - simplified structure with reduced spacing
    with st.container():
        # Header: Logo and name side-by-side (horizontal)
        header_col1, header_col2 = st.columns([1, 2.5], gap="small")
        
        with header_col1:
            # Logo - render directly without extra wrapper
            st.markdown(logo_html, unsafe_allow_html=True)
        
        with header_col2:
            st.markdown(f"""
            <div style="display: flex; align-items: center; height: 100%; margin: 0; padding: 0;">
                <h3 style="margin: 0; padding: 0; font-size: 1.2rem; font-weight: 700; color: #0f172a; line-height: 1.2;">{tool_name}</h3>
            </div>
            """, unsafe_allow_html=True)
        
        # Three scores in a single row - reduced spacing
        score_col1, score_col2, score_col3 = st.columns(3, gap="small")
        
        with score_col1:
            st.markdown(f"""
            <div style="
                text-align: center;
                background: {get_score_gradient(overall_score)};
                padding: 12px 6px;
                border-radius: 12px;
                box-shadow: 0 4px 14px rgba(0, 0, 0, 0.18);
                margin-bottom: 8px;
            ">
                <div style="
                    font-size: 1.6rem;
                    font-weight: 800;
                    color: white;
                    line-height: 1;
                    margin: 0 0 4px 0;
                    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.25);
                ">{overall_score}</div>
                <div style="
                    font-size: 0.65rem;
                    color: rgba(255,255,255,0.95);
                    font-weight: 600;
                    letter-spacing: 0.5px;
                    line-height: 1.2;
                    text-transform: uppercase;
                ">OVERALL</div>
            </div>
            """, unsafe_allow_html=True)
        
        with score_col2:
            st.markdown(f"""
            <div style="
                text-align: center;
                background: {get_score_gradient(perception_score)};
                padding: 12px 6px;
                border-radius: 12px;
                box-shadow: 0 4px 14px rgba(0, 0, 0, 0.18);
                margin-bottom: 8px;
            ">
                <div style="
                    font-size: 1.6rem;
                    font-weight: 800;
                    color: white;
                    line-height: 1;
                    margin: 0 0 4px 0;
                    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.25);
                ">{perception_score}</div>
                <div style="
                    font-size: 0.65rem;
                    color: rgba(255,255,255,0.95);
                    font-weight: 600;
                    letter-spacing: 0.5px;
                    line-height: 1.2;
                    text-transform: uppercase;
                ">PERCEPTION</div>
            </div>
            """, unsafe_allow_html=True)
        
        with score_col3:
            st.markdown(f"""
            <div style="
                text-align: center;
                background: {get_score_gradient(privacy_score)};
                padding: 12px 6px;
                border-radius: 12px;
                box-shadow: 0 4px 14px rgba(0, 0, 0, 0.18);
                margin-bottom: 8px;
            ">
                <div style="
                    font-size: 1.6rem;
                    font-weight: 800;
                    color: white;
                    line-height: 1;
                    margin: 0 0 4px 0;
                    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.25);
                ">{privacy_score}</div>
                <div style="
                    font-size: 0.65rem;
                    color: rgba(255,255,255,0.95);
                    font-weight: 600;
                    letter-spacing: 0.5px;
                    line-height: 1.2;
                    text-transform: uppercase;
                ">PRIVACY</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Buttons: View Details and Website side-by-side
        btn_col1, btn_col2 = st.columns(2, gap="small")
        with btn_col1:
            if st.button("View Details", key=f"view-{key_scope}-{idx}-{tool_name}", use_container_width=True, type="primary"):
                if df_raw is not None:
                    show_tool_details_modal(tool_name, row, df_raw)
                else:
                    st.warning("Details temporarily unavailable")
        with btn_col2:
            if url:
                st.link_button("Website", url, use_container_width=True)


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
    st.markdown(f"**Showing top {len(view)} of {len(df)} tools**")
    st.markdown("<br>", unsafe_allow_html=True)

    # Grid layout: 3 columns on desktop, responsive via CSS
    cols_per_row = 3
    
    for i in range(0, len(view), cols_per_row):
        cols = st.columns(cols_per_row, gap="large")
        for j, col in enumerate(cols):
            if i + j < len(view):
                with col:
                    render_tool_card(view.iloc[i + j], key_scope, i + j, df_raw)


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

