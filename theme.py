"""
theme.py  –  FinSet-inspired design system for CanteenOS.
Purple/violet palette matching the uploaded FinSet dashboard reference.

KEY TECHNICAL NOTES:
  - st.markdown(html, unsafe_allow_html=True) in Streamlit 1.52+ strips custom
    class attributes from <div>/<span> tags via its HTML sanitizer.
  - st.html(html) bypasses the sanitizer entirely and renders raw HTML safely.
  - Therefore: <style> blocks → st.markdown(unsafe_allow_html=True)
               all custom-class HTML components → st.html()
  - Accounting logic is NOT touched.
"""
import streamlit as st


# ---------------------------------------------------------------------------
# GLOBAL CSS  (injected once per page load via st.markdown)
# ---------------------------------------------------------------------------

GLOBAL_CSS = """
<style>
/* ── Font import ──────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Base reset ───────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}

/* ── App background ───────────────────────────────────────── */
.stApp {
    background-color: #EDE9FE !important;
}

/* ── Main content block ───────────────────────────────────── */
.block-container {
    padding-top: 3.25rem !important;
    padding-bottom: 2rem !important;
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
    max-width: 1320px !important;
    background-color: #EDE9FE !important;
}

/* ── Top header bar & sidebar controls ────────────────────── */
header[data-testid="stHeader"] {
    background-color: transparent !important;
    border-bottom: none !important;
    height: 2.75rem !important;
    z-index: 100 !important;
}

[data-testid="stSidebarCollapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    z-index: 1001 !important;
    color: #7C3AED !important;
}

[data-testid="stSidebarCollapseButton"] {
    color: #7C3AED !important;
}

/* ── Sidebar ──────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: none !important;
    box-shadow: 4px 0 24px rgba(124, 58, 237, 0.06) !important;
}

[data-testid="stSidebar"][aria-expanded="true"] {
    min-width: 230px !important;
    max-width: 230px !important;
}

[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
}

/* ── Sidebar radio — hide all built-in radio chrome ──────── */
[data-testid="stSidebar"] .stRadio > label {
    display: none !important;
}

[data-testid="stSidebar"] .stRadio > div {
    gap: 2px !important;
    flex-direction: column !important;
}

/* Hide the radio circle indicator (the ○ / ◉ dot) */
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label > div:first-child,
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label > span:first-child,
[data-testid="stSidebar"] [data-baseweb="radio"] > div:first-child,
[data-testid="stSidebar"] [data-baseweb="radio"] [data-testid="stRadioOptions"] > div:first-child {
    display: none !important;
}

[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
    display: flex !important;
    align-items: center !important;
    padding: 0.48rem 0.85rem 0.48rem 0.95rem !important;
    border-radius: 10px !important;
    font-size: 0.81rem !important;
    font-weight: 500 !important;
    color: #4B5563 !important;
    cursor: pointer !important;
    margin: 1px 8px !important;
    transition: background 0.15s !important;
    border: none !important;
    gap: 0 !important;
}

[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
    background: #F5F3FF !important;
    color: #7C3AED !important;
}

/* active nav item */
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) {
    background: #7C3AED !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    border: none !important;
}

/* hide the markdown paragraph spacing inside label */
[data-testid="stSidebar"] .stRadio span[data-testid="stMarkdownContainer"] p {
    margin: 0 !important;
    line-height: 1.4 !important;
}

/* hide the raw <input> element */
[data-testid="stSidebar"] input[type="radio"] {
    display: none !important;
}

/* hide any residual BaseWeb radio circle SVG */
[data-testid="stSidebar"] [data-baseweb="radio"] svg,
[data-testid="stSidebar"] [data-baseweb="radio"] [role="radio"] {
    display: none !important;
}

/* ── Streamlit native elements ────────────────────────────── */
h1, h2, h3, h4, h5, h6 {
    color: #1A1A2E !important;
    font-weight: 700 !important;
}

/* st.metric cards */
[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: none !important;
    border-radius: 16px !important;
    padding: 1.25rem 1.5rem !important;
    box-shadow: 0 2px 12px rgba(124, 58, 237, 0.08) !important;
}

[data-testid="stMetricLabel"] {
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    color: #6B7280 !important;
}

[data-testid="stMetricValue"] {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: #1A1A2E !important;
}

/* dataframes */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    border: none !important;
    overflow: hidden !important;
    box-shadow: 0 1px 8px rgba(124, 58, 237, 0.06) !important;
}

/* expanders */
[data-testid="stExpander"] {
    border: 1px solid #E9D5FF !important;
    border-radius: 12px !important;
    background: #FFFFFF !important;
}

[data-testid="stExpander"] summary {
    font-size: 0.84rem !important;
    font-weight: 600 !important;
    color: #374151 !important;
    padding: 0.75rem 1rem !important;
}

/* alerts */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    font-size: 0.84rem !important;
}

/* buttons */
.stButton > button {
    border-radius: 10px !important;
    font-size: 0.84rem !important;
    font-weight: 600 !important;
    background: #7C3AED !important;
    color: #FFFFFF !important;
    border: none !important;
    padding: 0.5rem 1.25rem !important;
    transition: background 0.15s !important;
}
.stButton > button:hover {
    background: #6D28D9 !important;
}
.stButton > button[kind="secondary"] {
    background: #F5F3FF !important;
    color: #7C3AED !important;
    border: 1px solid #DDD6FE !important;
}

/* tabs */
[data-testid="stTabs"] [role="tab"] {
    font-size: 0.84rem !important;
    font-weight: 600 !important;
    color: #6B7280 !important;
}

[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: #7C3AED !important;
    border-bottom-color: #7C3AED !important;
}

/* form labels */
.stTextInput label, .stNumberInput label, .stSelectbox label,
.stDateInput label, .stCheckbox label {
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    color: #374151 !important;
}

/* inputs */
.stTextInput input, .stNumberInput input, .stSelectbox select {
    border-radius: 8px !important;
    border-color: #DDD6FE !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: #7C3AED !important;
    box-shadow: 0 0 0 2px rgba(124,58,237,0.15) !important;
}

/* horizontal rule */
hr {
    border-color: #DDD6FE !important;
    margin: 1rem 0 !important;
}

/* captions */
[data-testid="stCaptionContainer"] {
    color: #6B7280 !important;
    font-size: 0.78rem !important;
}

/* selectbox */
[data-testid="stSelectbox"] > div > div {
    border-radius: 8px !important;
    border-color: #DDD6FE !important;
}

/* line chart and bar chart backgrounds */
[data-testid="stArrowVegaLiteChart"],
[data-testid="stVegaLiteChart"] {
    background: #FFFFFF !important;
    border-radius: 16px !important;
    padding: 0.5rem !important;
    box-shadow: 0 2px 12px rgba(124, 58, 237, 0.08) !important;
}

/* ── Custom component styles ──────────────────────────────── */

/* ── Page header ─────────────────────────────────────────── */
.cos-page-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    padding-bottom: 1.25rem;
    margin-bottom: 1.5rem;
}
.cos-page-title {
    font-size: 1.6rem;
    font-weight: 800;
    color: #1A1A2E;
    line-height: 1.2;
    letter-spacing: -0.03em;
}
.cos-page-subtitle {
    font-size: 0.82rem;
    color: #6B7280;
    margin-top: 0.3rem;
    line-height: 1.5;
    font-weight: 400;
}
.cos-badge {
    display: inline-flex;
    align-items: center;
    background: #7C3AED;
    border-radius: 20px;
    padding: 0.3rem 1rem;
    font-size: 0.72rem;
    font-weight: 700;
    color: #FFFFFF;
    white-space: nowrap;
    letter-spacing: 0.04em;
}

/* ── Section header ──────────────────────────────────────── */
.cos-section-title {
    font-size: 0.98rem;
    font-weight: 700;
    color: #1A1A2E;
    margin: 0 0 0.1rem 0;
}
.cos-section-sub {
    font-size: 0.78rem;
    color: #6B7280;
    margin: 0 0 0.75rem 0;
    font-weight: 400;
}

/* ── KPI card ────────────────────────────────────────────── */
.cos-kpi-card {
    background: #FFFFFF;
    border: none;
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(124, 58, 237, 0.08);
    min-height: 110px;
}
.cos-kpi-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #6B7280;
    margin-bottom: 0.5rem;
}
.cos-kpi-value {
    font-size: 1.55rem;
    font-weight: 800;
    color: #1A1A2E;
    line-height: 1.1;
    letter-spacing: -0.03em;
    margin-bottom: 0.4rem;
}
.cos-kpi-trend {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 0.15rem 0.5rem;
    border-radius: 20px;
}
.cos-kpi-trend-up   { background: #D1FAE5; color: #065F46; }
.cos-kpi-trend-down { background: #FEE2E2; color: #991B1B; }
.cos-kpi-trend-neu  { background: #F3F4F6; color: #374151; }
.cos-kpi-sub {
    font-size: 0.72rem;
    color: #9CA3AF;
    margin-top: 0.3rem;
}
.cos-kpi-icon {
    position: absolute;
    top: 1rem;
    right: 1.1rem;
    width: 36px;
    height: 36px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    background: #F5F3FF;
}
/* accent color variants */
.kpi-purple .cos-kpi-icon { background: #EDE9FE; }
.kpi-green  .cos-kpi-icon { background: #D1FAE5; }
.kpi-blue   .cos-kpi-icon { background: #DBEAFE; }
.kpi-red    .cos-kpi-icon { background: #FEE2E2; }
.kpi-amber  .cos-kpi-icon { background: #FEF3C7; }

/* ── Process stepper ─────────────────────────────────────── */
.cos-stepper {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 0;
    background: #FFFFFF;
    border-radius: 16px;
    padding: 1rem 1.5rem;
    margin-bottom: 1.5rem;
    overflow-x: auto;
    box-shadow: 0 2px 12px rgba(124, 58, 237, 0.08);
}
.cos-step {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    flex-shrink: 0;
    padding: 0.1rem 0;
}
.cos-step-num {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: #7C3AED;
    color: #FFFFFF;
    font-size: 0.6rem;
    font-weight: 800;
    flex-shrink: 0;
}
.cos-step-label {
    font-size: 0.75rem;
    font-weight: 600;
    color: #374151;
    white-space: nowrap;
}
.cos-step-arrow {
    color: #C4B5FD;
    font-size: 0.85rem;
    margin: 0 0.6rem;
    flex-shrink: 0;
}

/* ── Performer list ──────────────────────────────────────── */
.cos-performer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.6rem 1rem;
    background: #F9F7FF;
    border-radius: 10px;
    margin-bottom: 0.4rem;
    font-size: 0.82rem;
}
.cos-performer-medal { font-size: 0.95rem; flex-shrink: 0; }
.cos-performer-name  { flex: 1; font-weight: 600; color: #1A1A2E; margin-left: 0.6rem; }
.cos-performer-value { font-weight: 700; color: #059669; }

/* ── Loss alert ──────────────────────────────────────────── */
.cos-alert {
    background: #FFFBEB;
    border: 1px solid #FDE68A;
    border-left: 4px solid #F59E0B;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 1rem;
}
.cos-alert-title {
    font-size: 0.84rem;
    font-weight: 700;
    color: #78350F;
    margin-bottom: 0.6rem;
}
.cos-alert-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;
}
.cos-loss-chip {
    background: #FEF2F2;
    border: 1px solid #FECACA;
    border-radius: 10px;
    padding: 0.5rem 0.9rem;
    min-width: 120px;
}
.cos-loss-chip-name  { font-size: 0.78rem; font-weight: 600; color: #7F1D1D; }
.cos-loss-chip-value { font-size: 0.72rem; color: #991B1B; margin-top: 1px; }

/* ── Working / formula box ───────────────────────────────── */
.cos-working {
    background: #F5F3FF;
    border: 1px solid #DDD6FE;
    border-left: 4px solid #7C3AED;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin: 0.6rem 0;
    font-size: 0.83rem;
    color: #2E1065;
    line-height: 1.8;
}

/* ── Status banners ──────────────────────────────────────── */
.cos-banner-pass {
    background: #F0FDF4;
    border: 1px solid #BBF7D0;
    border-left: 4px solid #16A34A;
    border-radius: 12px;
    padding: 0.8rem 1.1rem;
    font-size: 0.84rem;
    color: #14532D;
    font-weight: 600;
    margin-bottom: 1rem;
}
.cos-banner-fail {
    background: #FEF2F2;
    border: 1px solid #FECACA;
    border-left: 4px solid #DC2626;
    border-radius: 12px;
    padding: 0.8rem 1.1rem;
    font-size: 0.84rem;
    color: #7F1D1D;
    font-weight: 600;
    margin-bottom: 1rem;
}

/* ── Accounting statement ────────────────────────────────── */
.cos-acct-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.84rem;
    background: #FFFFFF;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(124, 58, 237, 0.07);
    margin-bottom: 1.25rem;
}
.cos-acct-table caption {
    font-size: 0.95rem;
    font-weight: 700;
    color: #1A1A2E;
    text-align: left;
    padding: 0.6rem 0 0.6rem 0;
    caption-side: top;
}
.cos-acct-table th {
    background: #F5F3FF;
    color: #7C3AED;
    font-weight: 700;
    padding: 0.65rem 1rem;
    text-align: left;
    border-bottom: 2px solid #DDD6FE;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.cos-acct-table th.r { text-align: right; }
.cos-acct-table td {
    padding: 0.5rem 1rem;
    color: #374151;
    border-bottom: 1px solid #F5F3FF;
}
.cos-acct-table td.r {
    text-align: right;
    font-variant-numeric: tabular-nums;
    font-family: 'Inter', monospace;
}
.cos-acct-table tr.row-total td {
    font-weight: 700;
    color: #1A1A2E;
    background: #EDE9FE;
    border-top: 2px solid #7C3AED;
    border-bottom: 2px solid #7C3AED;
}
.cos-acct-table tr.row-mid-sep td {
    border-top: 1px solid #DDD6FE;
    border-left: 1px solid #DDD6FE;
}

/* ── Consistency check rows ──────────────────────────────── */
.cos-check-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.7rem 1rem;
    border-radius: 10px;
    font-size: 0.83rem;
    color: #374151;
    margin-bottom: 0.5rem;
    background: #FAFAFA;
    border: 1px solid #E9D5FF;
}
.cos-check-pass { border-left: 4px solid #16A34A; }
.cos-check-fail { border-left: 4px solid #DC2626; }

/* ── Verification card ───────────────────────────────────── */
.cos-verify-card-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    padding: 1rem 1.25rem;
    background: #FFFFFF;
    border: 1px solid #E9D5FF;
    border-radius: 12px;
    margin-bottom: 0.5rem;
    box-shadow: 0 1px 6px rgba(124, 58, 237, 0.06);
}
.cos-verify-problem-id    { font-size: 0.68rem; font-weight: 700; letter-spacing: 0.08em; color: #7C3AED; text-transform: uppercase; }
.cos-verify-problem-title { font-size: 0.95rem; font-weight: 700; color: #1A1A2E; margin: 0.15rem 0; }
.cos-verify-ref           { font-size: 0.72rem; color: #9CA3AF; }
.cos-badge-pass {
    display: inline-flex; align-items: center; gap: 0.25rem;
    background: #D1FAE5; color: #065F46; border: 1px solid #A7F3D0;
    border-radius: 20px; padding: 0.25rem 0.8rem;
    font-size: 0.7rem; font-weight: 700; white-space: nowrap; flex-shrink: 0;
}
.cos-badge-fail {
    display: inline-flex; align-items: center; gap: 0.25rem;
    background: #FEE2E2; color: #7F1D1D; border: 1px solid #FECACA;
    border-radius: 20px; padding: 0.25rem 0.8rem;
    font-size: 0.7rem; font-weight: 700; white-space: nowrap; flex-shrink: 0;
}

/* ── Sidebar brand block ─────────────────────────────────── */
.cos-sidebar-logo {
    width: 38px;
    height: 38px;
    border-radius: 10px;
    background: #7C3AED;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    color: #FFFFFF;
    flex-shrink: 0;
    margin-right: 0.6rem;
}
.cos-sidebar-brand {
    display: flex;
    align-items: center;
    padding: 1.1rem 1rem 0.9rem 1rem;
    border-bottom: 1px solid #F3F0FF;
    margin-bottom: 0.4rem;
}
.cos-sidebar-brand-text {
    min-width: 0;
    overflow: hidden;
}
.cos-sidebar-brand-name {
    font-size: 1rem;
    font-weight: 800;
    color: #1A1A2E;
    letter-spacing: -0.02em;
    line-height: 1.2;
    white-space: nowrap;
}
.cos-sidebar-brand-sub {
    font-size: 0.63rem;
    color: #9CA3AF;
    font-weight: 400;
    margin-top: 0.1rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.cos-sidebar-section {
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: #C4B5FD;
    text-transform: uppercase;
    padding: 0.75rem 1rem 0.25rem 1rem;
}
.cos-sidebar-footer {
    margin: 1rem 0.75rem 0.75rem 0.75rem;
    padding: 0.75rem 1rem;
    background: #F5F3FF;
    border: 1px solid #DDD6FE;
    border-radius: 12px;
    font-size: 0.68rem;
    color: #9CA3AF;
    line-height: 1.65;
}
.cos-sidebar-footer-label { font-weight: 700; color: #7C3AED; margin-bottom: 0.2rem; }

/* ── Chart card wrapper ──────────────────────────────────── */
.cos-chart-card {
    background: #FFFFFF;
    border-radius: 16px;
    padding: 1.25rem 1.5rem 1rem 1.5rem;
    box-shadow: 0 2px 12px rgba(124, 58, 237, 0.08);
    margin-bottom: 1rem;
}
.cos-chart-title {
    font-size: 0.9rem;
    font-weight: 700;
    color: #1A1A2E;
    margin-bottom: 0.15rem;
}
.cos-chart-sub {
    font-size: 0.74rem;
    color: #6B7280;
    margin-bottom: 0.6rem;
}
</style>
"""


def inject_css():
    """Inject the global stylesheet. Call once at the top of app.py."""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _html(content: str):
    """Render raw HTML using st.html() — bypasses markdown sanitizer."""
    st.html(content)


# ---------------------------------------------------------------------------
# PAGE HEADER
# ---------------------------------------------------------------------------

def page_header(title: str, subtitle: str, badge: str = None):
    badge_html = (f'<div class="cos-badge">{badge}</div>' if badge else "")
    _html(f"""
    <div class="cos-page-header">
        <div>
            <div class="cos-page-title">{title}</div>
            <div class="cos-page-subtitle">{subtitle}</div>
        </div>
        {badge_html}
    </div>
    """)


# ---------------------------------------------------------------------------
# SECTION HEADER
# ---------------------------------------------------------------------------

def section_header(title: str, subtitle: str = ""):
    sub = f'<div class="cos-section-sub">{subtitle}</div>' if subtitle else ""
    _html(f'<div class="cos-section-title">{title}</div>{sub}')


# ---------------------------------------------------------------------------
# KPI CARDS  — uses st.columns() + st.html() per cell
# ---------------------------------------------------------------------------

def kpi_row(cards: list):
    """
    cards: list of dicts with keys:
        label, value, sub (opt), icon (opt), color_class (opt), trend (opt)
    trend: dict with keys: direction ('up'|'down'|'neutral'), text
    color_class: kpi-purple | kpi-green | kpi-blue | kpi-red | kpi-amber
    """
    cols = st.columns(len(cards))
    for col, card in zip(cols, cards):
        icon_html = (f'<div class="cos-kpi-icon">{card["icon"]}</div>'
                     if card.get("icon") else "")
        sub_html = ""
        if card.get("trend"):
            t = card["trend"]
            cls = {"up": "cos-kpi-trend-up", "down": "cos-kpi-trend-down"}.get(
                t.get("direction", "neutral"), "cos-kpi-trend-neu"
            )
            arrow = {"up": "↑", "down": "↓"}.get(t.get("direction", ""), "·")
            sub_html = f'<div class="cos-kpi-trend {cls}">{arrow} {t["text"]}</div>'
        elif card.get("sub"):
            sub_html = f'<div class="cos-kpi-sub">{card["sub"]}</div>'
        color = card.get("color_class", "kpi-purple")
        with col:
            st.html(f"""
            <div class="cos-kpi-card {color}">
                {icon_html}
                <div class="cos-kpi-label">{card['label']}</div>
                <div class="cos-kpi-value">{card['value']}</div>
                {sub_html}
            </div>
            """)


# ---------------------------------------------------------------------------
# PROCESS STEPPER
# ---------------------------------------------------------------------------

STEPPER_STEPS = [
    ("01", "Recipe & BOM"),
    ("02", "Cost Sheet"),
    ("03", "Batch + EBQ"),
    ("04", "Contribution"),
    ("05", "Break-Even"),
    ("06", "Daily Sales"),
    ("07", "Trading A/c"),
    ("08", "P&L"),
]


def process_stepper():
    """Render the horizontal accounting-flow stepper."""
    inner = ""
    for i, (num_label, label) in enumerate(STEPPER_STEPS):
        arrow = '<span class="cos-step-arrow">&#8594;</span>' if i < len(STEPPER_STEPS) - 1 else ""
        inner += f"""
        <div class="cos-step">
            <span class="cos-step-num">{num_label}</span>
            <span class="cos-step-label">{label}</span>
        </div>{arrow}"""
    st.html(f'<div class="cos-stepper">{inner}</div>')


# ---------------------------------------------------------------------------
# LOSS ALERT PANEL
# ---------------------------------------------------------------------------

def loss_alert_panel(losers: list):
    if not losers:
        return
    chips = ""
    for item in losers:
        chips += f"""
        <div class="cos-loss-chip">
            <div class="cos-loss-chip-name">&#x1F534; {item['name']}</div>
            <div class="cos-loss-chip-value">Profit/unit: {item['profit_per_unit']}</div>
        </div>"""
    count = len(losers)
    plural = "es" if count != 1 else ""
    st.html(f"""
    <div class="cos-alert">
        <div class="cos-alert-title">
            &#9888;&#xFE0F; Attention Required &mdash;
            {count} dish{plural} operating below full cost
        </div>
        <div class="cos-alert-chips">{chips}</div>
    </div>
    """)
    st.caption(
        "These dishes have positive contribution (help pay fixed costs) but their selling price "
        "does not cover the full absorbed overhead. Dropping them without also eliminating their "
        "fixed costs would *reduce* total profit."
    )


# ---------------------------------------------------------------------------
# TOP PERFORMERS
# ---------------------------------------------------------------------------

def top_performers_panel(performers: list, title: str = "Top Performing Dishes"):
    section_header(title)
    medals = ["🥇", "🥈", "🥉"]
    rows = ""
    for i, p in enumerate(performers):
        medal = medals[i] if i < 3 else f"{i+1}."
        rows += f"""
        <div class="cos-performer">
            <span class="cos-performer-medal">{medal}</span>
            <span class="cos-performer-name">{p['name']}</span>
            <span class="cos-performer-value">{p['value']}</span>
        </div>"""
    st.html(f'<div style="margin-bottom:0.5rem">{rows}</div>')


# ---------------------------------------------------------------------------
# WORKING / FORMULA BOX
# ---------------------------------------------------------------------------

def working_box(title: str, lines: list, expanded: bool = True):
    with st.expander(f"📐 Working — {title}", expanded=expanded):
        for ln in lines:
            st.markdown(ln)


# ---------------------------------------------------------------------------
# STATUS BANNER
# ---------------------------------------------------------------------------

def status_badge(text: str, positive: bool):
    cls  = "cos-banner-pass" if positive else "cos-banner-fail"
    icon = "&#10003;" if positive else "&#10007;"
    st.html(f'<div class="{cls}">{icon} {text}</div>')


# ---------------------------------------------------------------------------
# CONSISTENCY CHECK ROW
# ---------------------------------------------------------------------------

def check_row(ok: bool, text: str):
    cls  = "cos-check-pass" if ok else "cos-check-fail"
    icon = "&#10003;" if ok else "&#10007;"
    st.html(f'<div class="cos-check-row {cls}">{icon}&nbsp; {text}</div>')


# ---------------------------------------------------------------------------
# ACCOUNTING STATEMENT  (T-account rendered as HTML table)
# ---------------------------------------------------------------------------

def account_statement(title: str, acc: dict, caption_text: str = ""):
    rows_html = ""
    for dr_label, dr_amt, cr_label, cr_amt in acc["rows"]:
        dr_cell = dr_label or ""
        cr_cell = cr_label or ""
        dr_val  = _inr(dr_amt) if dr_amt is not None else ""
        cr_val  = _inr(cr_amt) if cr_amt is not None else ""
        rows_html += f"""<tr>
            <td>{dr_cell}</td>
            <td class="r">{dr_val}</td>
            <td class="row-mid-sep">{cr_cell}</td>
            <td class="r">{cr_val}</td>
        </tr>"""
    rows_html += f"""<tr class="row-total">
        <td><strong>Total</strong></td>
        <td class="r"><strong>{_inr(acc['total_dr'])}</strong></td>
        <td class="row-mid-sep"><strong>Total</strong></td>
        <td class="r"><strong>{_inr(acc['total_cr'])}</strong></td>
    </tr>"""
    cap = f"<caption>{title}</caption>" if title else ""
    st.html(f"""
    <table class="cos-acct-table">
        {cap}
        <thead><tr>
            <th>Particulars (Dr)</th><th class="r">Debit (&#8377;)</th>
            <th class="row-mid-sep">Particulars (Cr)</th><th class="r">Credit (&#8377;)</th>
        </tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
    """)
    if caption_text:
        st.caption(caption_text)


def _inr(v):
    """Format number as INR (simple version for HTML tables)."""
    if v is None:
        return "&mdash;"
    neg = v < 0
    s   = f"{abs(v):,.2f}"
    out = "&#8377;" + s
    return ("&minus;" + out) if neg else out


# ---------------------------------------------------------------------------
# COST SHEET TABLE
# ---------------------------------------------------------------------------

def cost_sheet_table(rows, with_unit=True):
    import pandas as pd
    data = []
    for r in rows:
        item = {"Particulars": r["label"], "Total (₹)": _fmt_inr_plain(r["total"])}
        if with_unit:
            item["₹ / unit"] = _fmt_inr_plain(r["per_unit"]) if r["per_unit"] is not None else "—"
        data.append(item)
    df        = pd.DataFrame(data)
    bold_rows = [i for i, r in enumerate(rows) if r["bold"]]

    def style(row):
        return ["font-weight:700;background:#EDE9FE" if row.name in bold_rows else "" for _ in row]

    st.dataframe(df.style.apply(style, axis=1), hide_index=True,
                 height=35 * (len(df) + 1) + 3, use_container_width=True)


def _fmt_inr_plain(v):
    if v is None:
        return "—"
    neg = v < 0
    s   = f"{abs(v):,.2f}"
    out = "₹" + s
    return ("-" + out) if neg else out


# ---------------------------------------------------------------------------
# VERIFICATION CARD HEADER
# ---------------------------------------------------------------------------

def verify_card_header(problem_id: str, title: str, component: str,
                       all_pass: bool, reference: str):
    badge = (f'<span class="cos-badge-pass">&#10003; All figures match</span>'
             if all_pass else
             f'<span class="cos-badge-fail">&#10007; Mismatch found</span>')
    st.html(f"""
    <div class="cos-verify-card-header">
        <div>
            <div class="cos-verify-problem-id">{problem_id} &middot; {component}</div>
            <div class="cos-verify-problem-title">{title}</div>
            <div class="cos-verify-ref">Source: {reference}</div>
        </div>
        {badge}
    </div>
    """)
