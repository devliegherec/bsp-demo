"""Configuration and constants for the Oral Cavity Tumors Dashboard."""

# Color palette
COLOR_TEAL = '#1d9e75'
COLOR_BLUE = '#378add'
COLOR_AMBER = '#ef9f27'
COLOR_RED = '#e24b4a'
COLOR_GRAY = '#888780'
COLOR_PURP = '#7f77dd'
COLOR_GREEN = '#639922'

# CSS styling
STYLES = """
<style>
    [data-testid="stSidebar"] { width: 280px !important; }
    [data-testid="stSidebar"] > div:first-child { width: 280px !important; }
    .metric-card {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
    .metric-value { font-size: 28px; font-weight: 600; color: #1a1a2e; }
    .metric-label { font-size: 12px; color: #6c757d; margin-top: 2px; }
    .metric-sub { font-size: 11px; color: #adb5bd; margin-top: 1px; }
    .badge-pos { background:#fde8e8; color:#c0392b; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:600; }
    .badge-close { background:#fef3cd; color:#856404; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:600; }
    .badge-free { background:#d1fae5; color:#065f46; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:600; }
    div[data-testid="stMetricValue"] { font-size: 28px !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] { padding: 8px 20px; font-size: 13px; }
</style>
"""
