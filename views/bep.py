"""Component 3a : Marginal costing and Break-Even Point per counter (Module 4)."""
import pandas as pd
import streamlit as st

import costing as cx
import db
import services as sv
from ui import inr, num, pct, month_label
from theme import (
    page_header, section_header, kpi_row, working_box, status_badge,
)


def render(conn, month):
    page_header(
        "Break-Even Analysis",
        "Component 3 · Module 4 · Variable cost per dish comes from Component 1 (BOM) and "
        "Component 2 (set-up per unit at EBQ); sales mix comes from the daily sales.",
        badge="Component 3",
    )

    mc       = sv.month_costing(conn, month)
    counters = mc["counters"]
    section_header("Select Counter")
    cid    = st.selectbox("Counter", list(counters), format_func=counters.get,
                          label_visibility="collapsed")
    target = st.number_input("Target profit for the month (₹)",
                             min_value=0.0, value=0.0, step=1000.0)
    res    = sv.counter_bep(mc, cid, target)

    section_header(f"{counters[cid]} — {month_label(month)}")
    dishes = [u for u in mc["dishes"].values() if u["dish"]["counter_id"] == cid]
    if not dishes:
        st.info("No dishes on this counter yet.")
        return

    # ── Step 1 : contribution per dish ───────────────────────────────────────
    section_header("Step 1 · Contribution per Dish",
                   "Contribution = Selling price − Variable cost")
    rows = []
    for u in dishes:
        price = u["dish"]["selling_price"]
        rows.append({
            "Dish":              u["dish"]["name"],
            "Selling Price":     inr(price),
            "Material":          inr(u["dm_unit"]),
            "Labour":            inr(u["dl_unit"]),
            "Packaging":         inr(u["de_unit"]),
            "Gas/Fuel":          inr(u["voh_unit"]),
            "Set-up @EBQ":       inr(u["setup_unit"]),
            "Variable Cost":     inr(u["variable_cost"]),
            "Contribution/Unit": inr(u["contribution"]),
            "P/V Ratio":         pct(u["contribution"] / price if price else 0),
            "Units Sold":        f"{u['qty']:,}",
        })
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

    for u in dishes:
        if u["variable_cost"] >= u["dish"]["selling_price"]:
            st.warning(f"{u['dish']['name']}: variable cost {inr(u['variable_cost'])} is not below the "
                       f"selling price {inr(u['dish']['selling_price'])} — every sale adds to the loss.")

    if res["total_sales"] <= 0:
        st.info("No sales recorded for this counter in the selected month, so the sales mix is unknown.")
        return

    # ── Step 2 : counter fixed cost ───────────────────────────────────────────
    st.markdown("---")
    section_header("Step 2 · Fixed Cost of the Counter")
    pool  = mc["pools"][cid]
    app   = mc["apportioned"][cid]
    frows = [{
        "Function":                               f,
        "Allocated directly (₹)":                inr(pool[f], 0),
        "Common (apportioned on labour hrs) (₹)": inr(app[f], 0),
        "Total (₹)":                              inr(pool[f] + app[f], 0),
    } for f in sv.FUNCTIONS]
    frows.append({
        "Function":                               "FIXED COST (F)",
        "Allocated directly (₹)":                inr(sum(pool.values()), 0),
        "Common (apportioned on labour hrs) (₹)": inr(sum(app.values()), 0),
        "Total (₹)":                              inr(res["fixed_cost"], 0),
    })
    st.dataframe(pd.DataFrame(frows), hide_index=True, use_container_width=True)

    # ── Step 3 : composite BEP ────────────────────────────────────────────────
    st.markdown("---")
    section_header("Step 3 · Break-Even Point of the Counter", "Sales-mix (composite) method")

    if not res["feasible"]:
        st.error("Total contribution is zero or negative at the current prices and costs, "
                 "so this counter cannot break even. Raise prices or cut variable cost.")
        return

    working_box("Break-even (sales-mix method)", [
        "**Formulas (Module 4, slides 38-41):** Contribution = Sales − Variable cost; "
        "P/V ratio = Contribution ÷ Sales; BEP (₹) = Fixed cost ÷ P/V ratio; "
        "Margin of safety = Actual sales − BEP sales; Profit = Contribution − Fixed cost",
        f"Total sales = **{inr(res['total_sales'], 0)}**",
        f"Total contribution = Σ(contribution/unit × units sold) = **{inr(res['total_contribution'], 0)}**",
        f"P/V ratio = {inr(res['total_contribution'], 0)} ÷ {inr(res['total_sales'], 0)} = **{pct(res['pv_ratio'])}**",
        f"Fixed cost F = **{inr(res['fixed_cost'], 0)}**",
        f"BEP sales = {inr(res['fixed_cost'], 0)} ÷ {num(res['pv_ratio'], 4)} = **{inr(res['bep_sales'], 0)}**",
        f"Margin of safety = {inr(res['total_sales'], 0)} − {inr(res['bep_sales'], 0)} = "
        f"**{inr(res['mos_sales'], 0)}** ({pct(res['mos_pct'])} of sales)",
        f"Profit = {inr(res['total_contribution'], 0)} − {inr(res['fixed_cost'], 0)} = **{inr(res['profit'], 0)}**",
        f"Sales needed for target profit {inr(target, 0)} = (F + target) ÷ P/V = **{inr(res['target_sales'], 0)}**",
    ])

    # KPIs
    kpi_row([
        {"label": "BEP Sales",        "value": inr(res["bep_sales"], 0),   "icon": "⚖️", "color_class": "kpi-indigo"},
        {"label": "Actual Sales",     "value": inr(res["total_sales"], 0), "icon": "💰", "color_class": "kpi-blue"},
        {"label": "Margin of Safety", "value": pct(res["mos_pct"]),        "icon": "📏", "color_class": "kpi-green"
         if res["mos_sales"] >= 0 else "kpi-amber"},
        {"label": "Profit / (Loss)",  "value": inr(res["profit"], 0),      "icon": "📈", "color_class": "kpi-green"
         if res["profit"] >= 0 else "kpi-red"},
    ])

    if res["mos_sales"] >= 0:
        status_badge(f"{counters[cid]} is **above** break-even this month.", positive=True)
    else:
        status_badge(f"{counters[cid]} is **below** break-even — sales are {inr(-res['mos_sales'], 0)} "
                     "short of covering fixed cost.", positive=False)

    # Dish-level BEP split
    brows = [{
        "Dish":           r["name"],
        "Sales Mix":      pct(r["mix_pct"], 1),
        "BEP Sales (₹)":  inr(r["bep_sales"], 0),
        "BEP Units":      num(r["bep_units"], 0),
        "Actual Units":   f"{r['qty']:,}",
    } for r in res["rows"]]
    section_header("Break-Even Split by Dish", "At the current sales mix")
    st.dataframe(pd.DataFrame(brows), hide_index=True, use_container_width=True)

    # ── Break-Even Chart ───────────────────────────────────────────────────────
    section_header("Break-Even Chart",
                   "Revenue and total cost lines cross at the break-even sales value")
    top  = res["total_sales"] * 1.3
    pts  = [0, res["bep_sales"], res["total_sales"], top]
    chart = pd.DataFrame({
        "Sales (₹)":  pts,
        "Revenue":    pts,
        "Total cost": [res["fixed_cost"] + (1 - res["pv_ratio"]) * s for s in pts],
        "Fixed cost": [res["fixed_cost"]] * 4,
    }).set_index("Sales (₹)")
    st.line_chart(chart)

    # ── Single-dish BEP ───────────────────────────────────────────────────────
    st.markdown("---")
    section_header("Single-Dish Break-Even (Textbook Form)",
                   "Same formulas for one dish, using the fixed cost you type — as in the class problem on slide 41.")
    names = {u["dish"]["id"]: u["dish"]["name"] for u in dishes}
    did   = st.selectbox("Dish", list(names), format_func=names.get,
                         key=f"bep_dish_{cid}")
    ud    = mc["dishes"][did]
    fixed = st.number_input(
        "Fixed cost for this dish (₹)", min_value=0.0,
        value=float(round(res["fixed_cost"] * ud["qty"] * ud["dish"]["selling_price"] / res["total_sales"]))
              if res["total_sales"] else 0.0,
        step=500.0, key=f"bep_fixed_{cid}_{did}_{month}",
        help="Default = the dish's share of the counter's fixed cost by sales value.",
    )
    one = cx.bep(ud["dish"]["selling_price"], ud["variable_cost"], fixed, ud["qty"], target)
    if not one["feasible"]:
        st.error("Contribution per unit is zero or negative — no break-even point exists.")
    else:
        kpi_row([
            {"label": "Selling Price", "value": inr(ud["dish"]["selling_price"]), "icon": "🏷️", "color_class": "kpi-blue"},
            {"label": "Variable Cost", "value": inr(ud["variable_cost"]),         "icon": "📦", "color_class": "kpi-indigo"},
            {"label": "Contribution",  "value": inr(one["contribution_per_unit"]), "icon": "📈", "color_class": "kpi-green"},
        ])
        kpi_row([
            {"label": "Fixed Cost",    "value": inr(fixed, 0),                    "icon": "🏢", "color_class": "kpi-amber"},
            {"label": "BEP (Units)",   "value": f"{num(one['bep_units'], 0)} units", "icon": "⚖️", "color_class": "kpi-blue"},
            {"label": "BEP (Sales)",   "value": inr(one["bep_sales"], 0),        "icon": "💰", "color_class": "kpi-profit"},
        ])

        working_box(names[did], [
            f"Contribution per unit = {inr(ud['dish']['selling_price'])} − {inr(ud['variable_cost'])} = **{inr(one['contribution_per_unit'])}**",
            f"P/V ratio = {inr(one['contribution_per_unit'])} ÷ {inr(ud['dish']['selling_price'])} = **{pct(one['pv_ratio'])}**",
            f"BEP units = {inr(fixed, 0)} ÷ {inr(one['contribution_per_unit'])} = **{num(one['bep_units'], 0)} units**",
            f"BEP sales = {num(one['bep_units'], 0)} × {inr(ud['dish']['selling_price'])} = **{inr(one['bep_sales'], 0)}**",
            f"Margin of safety = {ud['qty']:,} − {num(one['bep_units'], 0)} = **{num(one['mos_units'], 0)} units** "
            f"({inr(one['mos_sales'], 0)})",
            f"Profit = {inr(one['total_contribution'], 0)} − {inr(fixed, 0)} = **{inr(one['profit'], 0)}**",
            f"Units for target profit = ({inr(fixed, 0)} + {inr(target, 0)}) ÷ {inr(one['contribution_per_unit'])} = **{num(one['target_units'], 0)}**",
        ])
