"""Dashboard - the month at a glance, all computed from the same linked data."""
import pandas as pd
import streamlit as st

import services as sv
from ui import inr, pct, month_label
from theme import (
    page_header, kpi_row, process_stepper, section_header,
    loss_alert_panel, top_performers_panel,
)


def render(conn, month):
    page_header(
        "Dashboard",
        f"College Canteen Costing & Financial Overview · {month_label(month)}",
        badge=month_label(month),
    )

    mc = sv.month_costing(conn, month)
    if not mc["qty"]:
        st.info("No sales recorded for this month yet. Add some on the **Daily Sales** page.")
        st.markdown("---")
        process_stepper()
        return

    acc = sv.month_accounts(conn, month, mc)
    total_cost = acc["sales"] - acc["net_profit"]

    # ── 1. KPI Row (Compact, 4 cards) ──────────────────────────────────────────
    net_pct = pct(acc["net_profit"] / acc["sales"]) if acc["sales"] else "—"
    gp_pct  = pct(acc["gross_profit"] / acc["sales"]) if acc["sales"] else "—"
    kpi_row([
        {"label": "Total Sales",  "value": inr(acc["sales"], 0),        "sub": f"{month_label(month)}",       "icon": "💰", "color_class": "kpi-blue"},
        {"label": "Total Cost",   "value": inr(total_cost, 0),          "sub": "Production + overheads",      "icon": "📦", "color_class": "kpi-indigo"},
        {"label": "Gross Profit", "value": inr(acc["gross_profit"], 0), "sub": f"GP Margin: {gp_pct}",        "icon": "📈", "color_class": "kpi-green"},
        {"label": "Net Profit",   "value": inr(acc["net_profit"], 0),   "sub": f"NP Margin: {net_pct}",        "icon": "✅", "color_class": "kpi-profit"
         if acc["net_profit"] >= 0 else "kpi-red"},
    ])

    # ── 2. Integrated Costing Flow (Stepper) ──────────────────────────────────
    section_header("Integrated Costing Flow", "The output of each component feeds the next in sequence")
    process_stepper()

    ds = list(mc["dishes"].values())

    # ── 3. Charts & Analytics Grid ────────────────────────────────────────────
    col_left, col_right = st.columns([3, 2], gap="medium")

    with col_left:
        section_header("Sales vs Cost", "Revenue vs full production cost after absorption")
        chart_data = pd.DataFrame({
            "Sales": [u["qty"] * u["dish"]["selling_price"] for u in ds],
            "Cost":  [u["qty"] * u["full_cost"]             for u in ds],
        }, index=[u["dish"]["name"] for u in ds])
        st.bar_chart(chart_data, color=["#3B5BDB", "#94A3B8"], height=280)

    with col_right:
        sorted_ds = sorted(ds, key=lambda u: u["profit_total"], reverse=True)
        top_performers = [
            {"name": u["dish"]["name"], "value": inr(u["profit_total"], 0)}
            for u in sorted_ds[:5]
        ]
        top_performers_panel(top_performers, title="Dish Profitability (Ranking)")

    # ── 4. Loss Alert (Attention Required) ─────────────────────────────────────
    losers = [{"name": u["dish"]["name"],
               "profit_per_unit": inr(u["profit_per_unit"])}
              for u in ds if u["profit_per_unit"] < 0]
    loss_alert_panel(losers)

    # ── 5. Dish Profitability Table ───────────────────────────────────────────
    section_header(
        "Dish Profitability",
        "Profitability per dish after absorption of overheads (full-cost basis)",
    )
    rows = []
    for u in ds:
        status = "LOSS" if u["profit_per_unit"] < 0 else "Profit"
        rows.append({
            "Dish":           u["dish"]["name"],
            "Price":          inr(u["dish"]["selling_price"]),
            "Variable Cost":  inr(u["variable_cost"]),
            "Contribution":   inr(u["contribution"]),
            "Profit / Unit":  inr(u["profit_per_unit"]),
            "Units":          f"{u['qty']:,}",
            "Total Profit":   inr(u["profit_total"], 0),
            "Status":         status,
        })
    df_prof = pd.DataFrame(rows)

    def highlight_status(row):
        is_loss = row["Status"] == "LOSS"
        return [
            "color: #DC2626; font-weight: 600;" if is_loss and col in ("Profit / Unit", "Total Profit", "Status")
            else "color: #059669; font-weight: 600;" if (not is_loss) and col in ("Profit / Unit", "Total Profit", "Status")
            else ""
            for col in row.index
        ]

    st.dataframe(
        df_prof.style.apply(highlight_status, axis=1),
        hide_index=True,
        use_container_width=True,
    )

    # Secondary details in an expander to keep main view concise
    with st.expander("🔍 View Detailed Cost Breakdown & Counter BEP Summary"):
        d_col1, d_col2 = st.columns(2)
        with d_col1:
            st.markdown("**Absorption Details by Dish**")
            detail_rows = [{
                "Dish":           u["dish"]["name"],
                "Counter":        u["dish"]["counter"],
                "Packaging & Set-up": inr(u["de_unit"] + u["setup_unit"]),
                "Absorbed O/H":   inr(sum(u["absorbed"].values())),
                "Cost of Sales":  inr(u["full_cost"]),
            } for u in ds]
            st.dataframe(pd.DataFrame(detail_rows), hide_index=True, use_container_width=True)

        with d_col2:
            st.markdown("**Break-Even Status by Counter**")
            brow = []
            for cid, name in mc["counters"].items():
                r = sv.counter_bep(mc, cid)
                if r["total_sales"] <= 0:
                    continue
                status = "Above BEP" if r["feasible"] and r["mos_sales"] >= 0 else "Below BEP"
                brow.append({
                    "Counter":          name,
                    "Sales":            inr(r["total_sales"], 0),
                    "BEP Sales":        inr(r["bep_sales"], 0) if r["bep_sales"] else "—",
                    "Margin of Safety": pct(r["mos_pct"])      if r["mos_pct"] is not None else "—",
                    "Profit/(Loss)":    inr(r["profit"], 0),
                    "Status":           status,
                })
            if brow:
                st.dataframe(pd.DataFrame(brow), hide_index=True, use_container_width=True)
