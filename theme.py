"""
theme.py  –  Shared design system for CanteenOS.

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
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800&display=swap');

/* ── Base reset ───────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}

/* ── App background ───────────────────────────────────────── */
.stApp {
    background-color: #F5F6FA !important;
}

/* ── Main content block ───────────────────────────────────── */
.block-container {
    padding-top: 1.25rem !important;
    padding-bottom: 2rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 1280px !important;
    background-color: #F5F6FA !important;
}

/* ── Top header bar ───────────────────────────────────────── */
header[data-testid="stHeader"] {
    background-color: #FFFFFF !important;
    border-bottom: 1px solid #E2E8F0 !important;
    height: 3rem !important;
}

/* ── Sidebar ──────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E2E8F0 !important;
}

[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
}

/* sidebar radio — hide the default radio circles, style as nav links */
[data-testid="stSidebar"] .stRadio > label {
    display: none !important;
}

[data-testid="stSidebar"] .stRadio > div {
    gap: 1px !important;
    flex-direction: column !important;
}

[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
    display: flex !important;
    align-items: center !important;
    padding: 0.45rem 1rem 0.45rem 1.25rem !important;
    border-radius: 6px !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    color: #374151 !important;
    cursor: pointer !important;
    margin: 1px 8px !important;
    transition: background 0.1s !important;
}

[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
    background: #F1F5F9 !important;
    color: #1E293B !important;
}

/* active nav item — the checked radio label */
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked),
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) {
    background: #EEF2FF !important;
    color: #3730A3 !important;
    font-weight: 600 !important;
    border-left: 3px solid #4F46E5 !important;
}

/* hide the actual radio dot */
[data-testid="stSidebar"] .stRadio span[data-testid="stMarkdownContainer"] p {
    margin: 0 !important;
}

[data-testid="stSidebar"] input[type="radio"] {
    display: none !important;
}

/* ── Streamlit native elements ────────────────────────────── */
h1, h2, h3, h4, h5, h6 {
    color: #1E293B !important;
    font-weight: 700 !important;
}

/* st.metric cards */
[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 10px !important;
    padding: 1rem 1.25rem !important;
}

[data-testid="stMetricLabel"] {
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    color: #64748B !important;
}

[data-testid="stMetricValue"] {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: #0F172A !important;
}

/* dataframes */
[data-testid="stDataFrame"] {
    border-radius: 8px !important;
    border: 1px solid #E2E8F0 !important;
    overflow: hidden !important;
}

/* expanders */
[data-testid="stExpander"] {
    border: 1px solid #E2E8F0 !important;
    border-radius: 8px !important;
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
    border-radius: 8px !important;
    font-size: 0.84rem !important;
}

/* buttons */
.stButton > button {
    border-radius: 6px !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
}

/* tabs */
[data-testid="stTabs"] [role="tab"] {
    font-size: 0.84rem !important;
    font-weight: 600 !important;
    color: #374151 !important;
}

[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: #3730A3 !important;
}

/* form labels */
.stTextInput label, .stNumberInput label, .stSelectbox label,
.stDateInput label, .stCheckbox label {
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    color: #374151 !important;
}

/* horizontal rule */
hr {
    border-color: #E2E8F0 !important;
    margin: 1rem 0 !important;
}

/* captions */
[data-testid="stCaptionContainer"] {
    color: #64748B !important;
    font-size: 0.78rem !important;
}

/* ── Custom component styles ──────────────────────────────── */

/* Page header */
.cos-page-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    padding-bottom: 1rem;
    margin-bottom: 1.25rem;
    border-bottom: 1px solid #E2E8F0;
}
.cos-page-title {
    font-size: 1.35rem;
    font-weight: 800;
    color: #0F172A;
    line-height: 1.2;
    letter-spacing: -0.02em;
}
.cos-page-subtitle {
    font-size: 0.8rem;
    color: #64748B;
    margin-top: 0.3rem;
    line-height: 1.5;
}
.cos-badge {
    display: inline-flex;
    align-items: center;
    background: #EEF2FF;
    border: 1px solid #C7D2FE;
    border-radius: 20px;
    padding: 0.25rem 0.75rem;
    font-size: 0.72rem;
    font-weight: 600;
    color: #3730A3;
    white-space: nowrap;
    margin-top: 0.2rem;
}

/* Section header */
.cos-section-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: #0F172A;
    margin: 0 0 0.1rem 0;
}
.cos-section-sub {
    font-size: 0.78rem;
    color: #64748B;
    margin: 0 0 0.75rem 0;
}

/* KPI card */
.cos-kpi-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    position: relative;
    overflow: hidden;
    height: 100%;
}
.cos-kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--kpi-accent, #3B5BDB);
    border-radius: 10px 10px 0 0;
}
.cos-kpi-label {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    color: #64748B;
    margin-bottom: 0.4rem;
}
.cos-kpi-value {
    font-size: 1.45rem;
    font-weight: 800;
    color: #0F172A;
    line-height: 1.1;
    margin-bottom: 0.3rem;
    letter-spacing: -0.02em;
}
.cos-kpi-sub {
    font-size: 0.72rem;
    color: #94A3B8;
}
.cos-kpi-icon {
    position: absolute;
    top: 0.9rem; right: 1rem;
    font-size: 1rem;
    opacity: 0.3;
}
.kpi-blue   { --kpi-accent: #3B5BDB; }
.kpi-indigo { --kpi-accent: #4F46E5; }
.kpi-green  { --kpi-accent: #059669; }
.kpi-profit { --kpi-accent: #0EA5E9; }
.kpi-red    { --kpi-accent: #DC2626; }
.kpi-amber  { --kpi-accent: #D97706; }

/* Process stepper */
.cos-stepper {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 0;
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 0.9rem 1.25rem;
    margin-bottom: 1.25rem;
    overflow-x: auto;
}
.cos-step {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    flex-shrink: 0;
    padding: 0.1rem 0;
}
.cos-step-num {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: #3B5BDB;
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
    color: #CBD5E1;
    font-size: 0.8rem;
    margin: 0 0.5rem;
    flex-shrink: 0;
    font-weight: 400;
}

/* Performer list */
.cos-performer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.55rem 0.9rem;
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 7px;
    margin-bottom: 0.4rem;
    font-size: 0.82rem;
}
.cos-performer-medal { font-size: 0.95rem; flex-shrink: 0; }
.cos-performer-name  { flex: 1; font-weight: 600; color: #1E293B; margin-left: 0.6rem; }
.cos-performer-value { font-weight: 700; color: #059669; }

/* Loss alert */
.cos-alert {
    background: #FFFBEB;
    border: 1px solid #FDE68A;
    border-left: 4px solid #F59E0B;
    border-radius: 8px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 1rem;
}
.cos-alert-title {
    font-size: 0.82rem;
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
    border-radius: 7px;
    padding: 0.45rem 0.85rem;
    min-width: 120px;
}
.cos-loss-chip-name  { font-size: 0.78rem; font-weight: 600; color: #7F1D1D; }
.cos-loss-chip-value { font-size: 0.72rem; color: #991B1B; margin-top: 1px; }

/* Working / formula box */
.cos-working {
    background: #F0F7FF;
    border: 1px solid #BFDBFE;
    border-left: 4px solid #3B5BDB;
    border-radius: 8px;
    padding: 0.9rem 1.1rem;
    margin: 0.6rem 0;
    font-size: 0.83rem;
    color: #1E3A5F;
    line-height: 1.75;
}

/* Status banners */
.cos-banner-pass {
    background: #F0FDF4;
    border: 1px solid #BBF7D0;
    border-left: 4px solid #16A34A;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    font-size: 0.84rem;
    color: #14532D;
    font-weight: 600;
    margin-bottom: 1rem;
}
.cos-banner-fail {
    background: #FEF2F2;
    border: 1px solid #FECACA;
    border-left: 4px solid #DC2626;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    font-size: 0.84rem;
    color: #7F1D1D;
    font-weight: 600;
    margin-bottom: 1rem;
}

/* Accounting statement */
.cos-acct-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.84rem;
    background: #FFFFFF;
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid #E2E8F0;
    margin-bottom: 1.25rem;
}
.cos-acct-table caption {
    font-size: 0.95rem;
    font-weight: 700;
    color: #0F172A;
    text-align: left;
    padding: 0.6rem 0 0.6rem 0;
    caption-side: top;
}
.cos-acct-table th {
    background: #F8FAFC;
    color: #374151;
    font-weight: 600;
    padding: 0.6rem 1rem;
    text-align: left;
    border-bottom: 2px solid #E2E8F0;
    font-size: 0.8rem;
}
.cos-acct-table th.r { text-align: right; }
.cos-acct-table td {
    padding: 0.5rem 1rem;
    color: #374151;
    border-bottom: 1px solid #F1F5F9;
}
.cos-acct-table td.r {
    text-align: right;
    font-variant-numeric: tabular-nums;
    font-family: 'Inter', monospace;
}
.cos-acct-table tr.row-total td {
    font-weight: 700;
    color: #0F172A;
    background: #EEF2FF;
    border-top: 2px solid #3B5BDB;
    border-bottom: 2px solid #3B5BDB;
}
.cos-acct-table tr.row-mid-sep td {
    border-top: 1px solid #E2E8F0;
    border-left: 1px solid #E2E8F0;
}

/* Consistency check rows */
.cos-check-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.65rem 1rem;
    border-radius: 8px;
    font-size: 0.83rem;
    color: #374151;
    margin-bottom: 0.5rem;
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
}
.cos-check-pass { border-left: 4px solid #16A34A; }
.cos-check-fail { border-left: 4px solid #DC2626; }

/* Verification card */
.cos-verify-card-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    padding: 0.9rem 1.1rem;
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    margin-bottom: 0.5rem;
}
.cos-verify-problem-id    { font-size: 0.68rem; font-weight: 700; letter-spacing: 0.08em; color: #64748B; text-transform: uppercase; }
.cos-verify-problem-title { font-size: 0.95rem; font-weight: 700; color: #0F172A; margin: 0.15rem 0; }
.cos-verify-ref           { font-size: 0.72rem; color: #94A3B8; }
.cos-badge-pass {
    display: inline-flex; align-items: center; gap: 0.25rem;
    background: #F0FDF4; color: #14532D; border: 1px solid #BBF7D0;
    border-radius: 20px; padding: 0.2rem 0.7rem;
    font-size: 0.7rem; font-weight: 700; white-space: nowrap; flex-shrink: 0;
}
.cos-badge-fail {
    display: inline-flex; align-items: center; gap: 0.25rem;
    background: #FEF2F2; color: #7F1D1D; border: 1px solid #FECACA;
    border-radius: 20px; padding: 0.2rem 0.7rem;
    font-size: 0.7rem; font-weight: 700; white-space: nowrap; flex-shrink: 0;
}

/* Sidebar brand block */
.cos-sidebar-brand {
    padding: 1.1rem 1.25rem 1rem 1.25rem;
    border-bottom: 1px solid #E2E8F0;
    margin-bottom: 0.25rem;
}
.cos-sidebar-brand-name {
    font-size: 1.1rem;
    font-weight: 800;
    color: #0F172A;
    letter-spacing: -0.02em;
}
.cos-sidebar-brand-sub {
    font-size: 0.7rem;
    color: #94A3B8;
    font-weight: 500;
    margin-top: 0.1rem;
}
.cos-sidebar-section {
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: #94A3B8;
    text-transform: uppercase;
    padding: 0.9rem 1.25rem 0.3rem 1.25rem;
}
.cos-sidebar-footer {
    margin: 1rem 0.75rem 0.75rem 0.75rem;
    padding: 0.65rem 0.9rem;
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    font-size: 0.68rem;
    color: #94A3B8;
    line-height: 1.6;
}
.cos-sidebar-footer-label { font-weight: 700; color: #64748B; margin-bottom: 0.2rem; }
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
    badge_html = (f'<div class="cos-badge">📌 {badge}</div>' if badge else "")
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
        label, value, sub (opt), icon (opt), color_class (opt)
    color_class: kpi-blue | kpi-indigo | kpi-green | kpi-profit | kpi-red | kpi-amber
    """
    cols = st.columns(len(cards))
    for col, card in zip(cols, cards):
        icon_html = (f'<div class="cos-kpi-icon">{card["icon"]}</div>'
                     if card.get("icon") else "")
        sub_html  = (f'<div class="cos-kpi-sub">{card["sub"]}</div>'
                     if card.get("sub") else "")
        color     = card.get("color_class", "kpi-blue")
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
        return ["font-weight:700;background:#EEF2FF" if row.name in bold_rows else "" for _ in row]

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
