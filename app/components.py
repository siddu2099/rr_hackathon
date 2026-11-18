"""
Reusable UI components for SupeRR Selector Season 2 Dashboard.
Provides clean HTML/CSS cards, metric badges, and layout helpers.
"""
from typing import Optional, Dict, Any
import streamlit as st

from app.config import (
    COLOR_NAVY_BG,
    COLOR_CARD_BG,
    COLOR_CARD_BORDER,
    COLOR_BATTING,
    COLOR_BOWLING,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED,
    COLOR_EMERALD,
    COLOR_AMBER
)


def apply_custom_css():
    """Inject custom CSS for dark sports-analytics aesthetic."""
    st.markdown(f"""
    <style>
        /* Global Background & Text */
        .stApp {{
            background-color: {COLOR_NAVY_BG};
            color: {COLOR_TEXT_PRIMARY};
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }}
        
        /* Metric Card Container */
        .rr-kpi-card {{
            background-color: {COLOR_CARD_BG};
            border: 1px solid {COLOR_CARD_BORDER};
            border-radius: 8px;
            padding: 16px 20px;
            margin-bottom: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
            transition: border-color 0.2s ease;
        }}
        .rr-kpi-card:hover {{
            border-color: {COLOR_BOWLING};
        }}
        .rr-kpi-title {{
            font-size: 0.85rem;
            font-weight: 600;
            color: {COLOR_TEXT_MUTED};
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 4px;
        }}
        .rr-kpi-value {{
            font-size: 1.85rem;
            font-weight: 800;
            color: {COLOR_TEXT_PRIMARY};
            line-height: 1.1;
            margin-bottom: 4px;
        }}
        .rr-kpi-sub {{
            font-size: 0.78rem;
            color: {COLOR_TEXT_MUTED};
        }}
        .rr-kpi-delta-pos {{
            color: {COLOR_EMERALD};
            font-weight: 700;
            font-size: 0.85rem;
        }}
        .rr-kpi-delta-neg {{
            color: {COLOR_BATTING};
            font-weight: 700;
            font-size: 0.85rem;
        }}
        
        /* Header Box */
        .rr-header-box {{
            padding: 8px 0 20px 0;
            border-bottom: 1px solid {COLOR_CARD_BORDER};
            margin-bottom: 24px;
        }}
        .rr-header-badge {{
            display: inline-block;
            background: rgba(225, 29, 72, 0.15);
            color: {COLOR_BATTING};
            border: 1px solid {COLOR_BATTING};
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            margin-bottom: 8px;
        }}
        .rr-header-title {{
            font-size: 2.1rem;
            font-weight: 800;
            color: {COLOR_TEXT_PRIMARY};
            margin: 0;
            line-height: 1.2;
        }}
        .rr-header-subtitle {{
            font-size: 1.0rem;
            color: {COLOR_TEXT_MUTED};
            margin-top: 6px;
        }}
        
        /* Player Card */
        .rr-player-card {{
            background: {COLOR_CARD_BG};
            border: 1px solid {COLOR_CARD_BORDER};
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 16px;
        }}
        .rr-player-rank {{
            font-size: 1.2rem;
            font-weight: 800;
            color: {COLOR_BATTING};
        }}
        .rr-player-name {{
            font-size: 1.5rem;
            font-weight: 800;
            color: {COLOR_TEXT_PRIMARY};
            margin-bottom: 8px;
        }}
        
        /* Custom tables */
        div[data-testid="stDataFrame"] {{
            border: 1px solid {COLOR_CARD_BORDER};
            border-radius: 8px;
            overflow: hidden;
        }}
    </style>
    """, unsafe_allow_html=True)


def render_header(title: str, subtitle: str, badge: str = "SupeRR Selector Season 2"):
    """Render unified page header."""
    apply_custom_css()
    st.markdown(f"""
    <div class="rr-header-box">
        <span class="rr-header-badge">{badge}</span>
        <h1 class="rr-header-title">{title}</h1>
        <div class="rr-header-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


def render_kpi(
    title: str,
    value: Any,
    subtext: str = "",
    delta: Optional[str] = None,
    delta_positive: bool = True,
    border_accent: Optional[str] = None
):
    """Render a standalone KPI card."""
    border_style = f"border-left: 4px solid {border_accent};" if border_accent else ""
    delta_html = ""
    if delta:
        delta_class = "rr-kpi-delta-pos" if delta_positive else "rr-kpi-delta-neg"
        delta_html = f"<span class='{delta_class}'>{delta}</span> • "
        
    st.markdown(f"""
    <div class="rr-kpi-card" style="{border_style}">
        <div class="rr-kpi-title">{title}</div>
        <div class="rr-kpi-value">{value}</div>
        <div class="rr-kpi-sub">{delta_html}{subtext}</div>
    </div>
    """, unsafe_allow_html=True)


def render_player_summary_card(profile: Dict[str, Any], role: str = "batter"):
    """Render rich player profile card with key metrics."""
    accent = COLOR_BATTING if role == "batter" else COLOR_BOWLING
    
    rank_str = f"Rank #{profile['rank']}" if profile['rank'] > 0 else "Qualified Contender"
    bpri_str = f"{profile['bpri']:.2f}" if profile['bpri'] > 0 else "N/A"
    
    st.markdown(f"""
    <div class="rr-player-card" style="border-left: 4px solid {accent};">
        <div style="display: flex; justify-content: space-between; align-items: baseline;">
            <div>
                <span class="rr-player-rank" style="color: {accent};">{rank_str}</span>
                <div class="rr-player-name">{profile['name']}</div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 0.8rem; color: {COLOR_TEXT_MUTED}; text-transform: uppercase;">BPRI Score</div>
                <div style="font-size: 1.8rem; font-weight: 800; color: {COLOR_TEXT_PRIMARY};">{bpri_str}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar_footer():
    """Render consistent repository and metadata links in sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"""
    <div style="font-size: 0.78rem; color: {COLOR_TEXT_MUTED};">
        <b>SupeRR Selector Season 2</b><br>
        Pressure Performance Analytics<br>
        Coverage: 867 Matches (2022–2026)<br>
        200,999 Deliveries • 26,735 Under Pressure<br>
        <br>
        <i>Rajasthan Royals Competitive Analytics</i>
    </div>
    """, unsafe_allow_html=True)
