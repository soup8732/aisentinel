"""
Logo service for fetching company logos using Clearbit Logo API.

This module provides functionality to fetch and cache company logos
for display in the dashboard tool cards.

Requirements:
    - requests library (already in requirements)
    - No API key needed for Clearbit Logo API (free tier)

Usage:
    from src.utils.logo_service import get_company_logo

    logo_url = get_company_logo("OpenAI")
    # Returns: https://logo.clearbit.com/openai.com
"""
from __future__ import annotations

from typing import Dict, Optional
import streamlit as st

# Mapping from tool names to company domains for Clearbit Logo API
# Format: "Tool Name" -> "company-domain.com"
TOOL_TO_DOMAIN: Dict[str, str] = {
    # Text & Chat Models
    "ChatGPT": "openai.com",
    "Claude": "anthropic.com",
    "Gemini": "google.com",
    "DeepSeek": "deepseek.com",
    "Mistral": "mistral.ai",
    "Jasper": "jasper.ai",
    "Copy.ai": "copy.ai",
    "Writesonic": "writesonic.com",
    "Lindy": "lindy.ai",
    
    # Coding & Dev Tools
    "GitHub Copilot": "github.com",
    "Amazon Q Developer": "amazon.com",
    "CodeWhisperer": "amazon.com",
    "Tabnine": "tabnine.com",
    "Tabby": "tabby.tabbyml.com",
    "Replit Ghostwriter": "replit.com",
    "Bolt": "bolt.new",
    "Loveable": "lovable.dev",
    "JetBrains AI Assistant": "jetbrains.com",
    "Cursor": "cursor.sh",
    "Codeium": "codeium.com",
    "Polycoder": "huggingface.co",  # Research model, using HuggingFace
    "AskCodi": "askcodi.com",
    "Sourcery": "sourcery.ai",
    "Greta": "greta.ai",
    
    # Image & Video Tools
    "Stability AI": "stability.ai",
    "RunwayML": "runwayml.com",
    "Midjourney": "midjourney.com",
    "DALL-E": "openai.com",
    "DreamStudio": "stability.ai",
    "OpenCV": "opencv.org",
    "Adobe Firefly": "adobe.com",
    "Pika Labs": "pika.art",
    "Luma Dream Machine": "lumalabs.ai",
    "Vidu": "vidu.ai",
    
    # Audio & Speech Tools
    "Whisper": "openai.com",
    "ElevenLabs": "elevenlabs.io",
    "Murf AI": "murf.ai",
    "PlayHT": "play.ht",
    "Speechify": "speechify.com",
    "Synthesys": "synthesys.io",
    "Animaker": "animaker.com",
    "Kits AI": "kits.ai",
    "WellSaid Labs": "wellsaidlabs.com",
    "Hume": "hume.ai",
    "DupDub": "dupdub.com",
}


def get_company_domain(tool_name: str) -> Optional[str]:
    """Get the company domain for a tool name.
    
    Args:
        tool_name: Name of the tool from taxonomy
        
    Returns:
        Company domain (e.g., "openai.com") or None if not found
    """
    return TOOL_TO_DOMAIN.get(tool_name)


def get_company_logo(tool_name: str, size: int = 64) -> Optional[str]:
    """Get the Clearbit logo URL for a company.
    
    Uses Clearbit Logo API: https://logo.clearbit.com/{domain}
    No API key required for basic usage.
    
    Args:
        tool_name: Name of the tool
        size: Logo size in pixels (default: 64)
        
    Returns:
        Logo URL string or None if domain not found
    """
    domain = get_company_domain(tool_name)
    if not domain:
        return None
    
    return f"https://logo.clearbit.com/{domain}?size={size}"


@st.cache_data(ttl=86400)  # Cache for 24 hours
def get_logo_url_cached(tool_name: str, size: int = 64) -> Optional[str]:
    """Get cached logo URL for a tool.
    
    Caches logo URLs for 24 hours to reduce redundant lookups.
    
    Args:
        tool_name: Name of the tool
        size: Logo size in pixels
        
    Returns:
        Logo URL string or None if domain not found
    """
    return get_company_logo(tool_name, size)


def get_logo_url(tool_name: str, size: int = 64) -> Optional[str]:
    """Get logo URL for a tool (for use with Streamlit's image display).
    
    Args:
        tool_name: Name of the tool
        size: Logo size in pixels
        
    Returns:
        Logo URL string or None if domain not found
    """
    return get_logo_url_cached(tool_name, size)


def get_logo_html(tool_name: str, size: int = 48, fallback_text: Optional[str] = None) -> str:
    """Generate HTML img tag for company logo with reliable fallback.
    
    Always returns HTML that will display either the logo or a styled fallback badge.
    Uses proper error handling to ensure fallback shows immediately if logo fails.
    
    Args:
        tool_name: Name of the tool
        size: Logo size in pixels
        fallback_text: Text to show if logo fails to load (defaults to tool name initials)
        
    Returns:
        HTML string with img tag and fallback that always displays something
    """
    logo_url = get_logo_url_cached(tool_name, size)
    fallback = fallback_text or tool_name[:2].upper()
    
    # Container ID for reliable error handling
    container_id = f"logo-{tool_name.lower().replace(' ', '-')}-{size}"
    
    if logo_url:
        # HTML with reliable error handling - fallback shows immediately on error
        return f"""
        <div id="{container_id}" style="
            width: {size}px;
            height: {size}px;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 14px;
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.08) 0%, rgba(139, 92, 246, 0.08) 100%);
            padding: 10px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
        ">
            <img 
                id="{container_id}-img"
                src="{logo_url}" 
                alt="{tool_name} logo"
                style="
                    max-width: calc(100% - 4px);
                    max-height: calc(100% - 4px);
                    width: auto;
                    height: auto;
                    object-fit: contain;
                    display: block;
                "
                onerror="
                    (function() {{
                        var img = document.getElementById('{container_id}-img');
                        var container = document.getElementById('{container_id}');
                        var fallback = container ? container.querySelector('.logo-fallback') : null;
                        if (img) img.style.display = 'none';
                        if (fallback) fallback.style.display = 'flex';
                    }})();
                "
                onload="
                    (function() {{
                        var img = document.getElementById('{container_id}-img');
                        var container = document.getElementById('{container_id}');
                        var fallback = container ? container.querySelector('.logo-fallback') : null;
                        if (img && img.complete && img.naturalHeight !== 0 && fallback) {{
                            fallback.style.display = 'none';
                        }}
                    }})();
                "
            />
            <div class="logo-fallback" style="
                display: none;
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                border-radius: 12px;
                background: linear-gradient(135deg, #00d4ff 0%, #8b5cf6 100%);
                color: white;
                font-weight: 700;
                font-size: {int(size * 0.4)}px;
                align-items: center;
                justify-content: center;
                text-align: center;
                box-shadow: 0 2px 10px rgba(0, 212, 255, 0.3);
            ">{fallback}</div>
        </div>
        """
    else:
        # No domain found, show styled fallback immediately
        return f"""
        <div style="
            width: {size}px;
            height: {size}px;
            border-radius: 14px;
            background: linear-gradient(135deg, #00d4ff 0%, #8b5cf6 100%);
            color: white;
            font-weight: 700;
            font-size: {int(size * 0.4)}px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 10px rgba(0, 212, 255, 0.3);
        ">{fallback}</div>
        """

