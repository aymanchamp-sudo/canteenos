"""
CanteenOS - College Canteen Costing & Financial Management System
FCA IA2 project (A11) | Modules 2 + 3 + 4

Run:   streamlit run app.py
"""
import streamlit as st

import db
import seed
import services as sv
from ui import month_label
from theme import inject_css
from views import accounts, batch, bep, dashboard, recipe, sales, verify

st.set_page_config(
    page_title="CanteenOS",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject global CSS — must be first after set_page_config
inject_css()


@st.cache_resource
def connection():
    conn = db.get_conn()
    if db.is_empty(conn):
        seed.seed(conn)
    return conn


conn = connection()

PAGES = {
    "Dashboard":                  dashboard,
    "Recipe & BOM → Cost Sheet":  recipe,
    "Batch Costing & EBQ":        batch,
    "Break-Even Analysis":        bep,
    "Daily Sales":                sales,
    "Monthly Trading & P&L":      accounts,
    "Textbook Verification":      verify,
}

NAV_GROUPS = [
    ("OVERVIEW",   ["Dashboard"]),
    ("COSTING",    ["Recipe & BOM → Cost Sheet", "Batch Costing & EBQ", "Break-Even Analysis"]),
    ("FINANCIALS", ["Daily Sales", "Monthly Trading & P&L"]),
    ("ACADEMIC",   ["Textbook Verification"]),
]

ICONS = {
    "Dashboard":                  "◉",
    "Recipe & BOM → Cost Sheet":  "📋",
    "Batch Costing & EBQ":        "⚙️",
    "Break-Even Analysis":        "⚖️",
    "Daily Sales":                "🧾",
    "Monthly Trading & P&L":      "📊",
    "Textbook Verification":      "✅",
}

# Build a flat ordered list maintaining group order — for single radio
all_labels = []
all_keys   = []
for _, items in NAV_GROUPS:
    for item in items:
        icon = ICONS.get(item, "·")
        all_labels.append(f"{icon}  {item}")
        all_keys.append(item)

# Initialise session state
if "page" not in st.session_state:
    st.session_state["page"] = "Dashboard"

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand logo + name (FinSet style)
    st.html("""
    <div class="cos-sidebar-brand">
        <div class="cos-sidebar-logo">🍽</div>
        <div class="cos-sidebar-brand-text">
            <div class="cos-sidebar-brand-name">CanteenOS</div>
            <div class="cos-sidebar-brand-sub">Costing &amp; Finance</div>
        </div>
    </div>
    """)

    # Section headers + single flat radio (CSS handles the grouped look)
    # We render section labels as st.html decorators, interleaved with the radio.
    # However, st.radio is atomic — we can't interleave HTML between radio options.
    # Solution: use st.radio for the full flat list, then render section labels
    # as absolute-positioned CSS based on item counts (fragile).
    # Better: inject group labels as disabled "header" options styled via CSS.

    # We use st.radio with the flat list. Section headers are shown above
    # via separate st.html calls, with the radio rendered per-section.
    # To keep tests passing (single session_state["page"] key), we map
    # from each section radio back to the flat all_keys list.

    current_page = st.session_state["page"]
    current_index = all_keys.index(current_page) if current_page in all_keys else 0

    selected_label = st.radio(
        "Navigation",
        all_labels,
        index=current_index,
        label_visibility="collapsed",
    )
    selected_page = all_keys[all_labels.index(selected_label)]
    if selected_page != st.session_state["page"]:
        st.session_state["page"] = selected_page
        st.rerun()

    # Reporting period
    st.markdown("---")
    st.html('<div class="cos-sidebar-section">REPORTING PERIOD</div>')
    months = sv.available_months(conn) or ["2026-11"]
    month  = st.selectbox(
        "Month",
        months,
        format_func=month_label,
        label_visibility="collapsed",
    )

    # Footer
    st.html("""
    <div class="cos-sidebar-footer">
        <div class="cos-sidebar-footer-label">FCA IA2 &middot; A11</div>
        <div>Modules 2, 3 &amp; 4</div>
        <div style="margin-top:0.3rem;">
            Comp 1: Recipe &rarr; Cost Sheet<br>
            Comp 2: Batch + EBQ<br>
            Comp 3: BEP + Accounts
        </div>
    </div>
    """)

# ── Render current page ───────────────────────────────────────────────────────
PAGES[st.session_state["page"]].render(conn, month)
