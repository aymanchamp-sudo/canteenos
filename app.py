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

# Build a flat ordered list of (display_label, page_key) for the radio
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
    # Brand
    st.html("""
    <div class="cos-sidebar-brand">
        <div class="cos-sidebar-brand-name">🍽️ CanteenOS</div>
        <div class="cos-sidebar-brand-sub">Costing &amp; Financial Management</div>
    </div>
    """)

    # Navigation via radio (CSS hides radio dots and styles items as nav links)
    current_index  = all_keys.index(st.session_state["page"]) if st.session_state["page"] in all_keys else 0
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
