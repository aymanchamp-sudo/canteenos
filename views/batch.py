"""Component 2 : Batch costing + Economic Batch Quantity (Module 4)."""
import pandas as pd
import streamlit as st

import costing as cx
import db
import services as sv
from ui import inr, num
from theme import page_header, section_header, kpi_row, working_box, status_badge


def render(conn, month):
    page_header(
        "Batch Costing & EBQ",
        "Component 2 · Module 4 · Uses the unit cost from Component 1; "
        "its EBQ feeds the variable cost used in Component 3.",
        badge="Component 2",
    )

    dishes  = db.df(conn, "SELECT id, name FROM dishes ORDER BY counter_id, id")
    names   = dict(zip(dishes["id"], dishes["name"]))
    section_header("Select Dish")
    dish_id = st.selectbox("Dish", list(names), format_func=names.get,
                           label_visibility="collapsed")
    u = sv.dish_unit_costs(conn, dish_id)
    d = u["dish"]

    # ── EBQ Inputs ────────────────────────────────────────────────────────────
    section_header("EBQ Inputs",
                   "Demand and holding cost must use the same time period. "
                   "The class example uses a year; a canteen cooks fresh food daily, so CanteenOS uses a day.")
    with st.form(f"ebq_{dish_id}"):
        c1, c2, c3 = st.columns(3)
        demand = c1.number_input("Demand per day  D (units)", min_value=0.0,
                                 value=float(d["demand_per_day"]), step=5.0)
        setup  = c2.number_input("Set-up cost per batch  S (₹)", min_value=0.0,
                                 value=float(d["setup_cost_per_batch"]), step=5.0)
        hold   = c3.number_input("Holding cost per unit per day  C (₹)", min_value=0.01,
                                 value=float(d["holding_cost_per_unit_per_day"]), step=0.1)
        if st.form_submit_button("💾  Save EBQ inputs", type="primary"):
            conn.execute("UPDATE dishes SET demand_per_day=?, setup_cost_per_batch=?, "
                         "holding_cost_per_unit_per_day=? WHERE id=?",
                         (demand, setup, hold, dish_id))
            conn.commit()
            st.rerun()

    e = u["ebq"]
    if d["demand_per_day"] <= 0:
        st.warning("Demand is zero, so there is no sensible batch size. Enter a demand above zero.")
        return

    # ── EBQ Result KPIs ───────────────────────────────────────────────────────
    st.markdown("---")
    section_header("Economic Batch Quantity (EBQ)",
                   "Formula: EBQ = √( 2 × D × S ÷ C )")
    kpi_row([
        {"label": "Daily Demand (D)",       "value": f"{num(d['demand_per_day'], 0)} units/day",
         "icon": "📦", "color_class": "kpi-blue"},
        {"label": "Set-up Cost (S)",        "value": inr(d["setup_cost_per_batch"]),
         "icon": "⚙️", "color_class": "kpi-indigo"},
        {"label": "Holding Cost (C)",       "value": f"{inr(d['holding_cost_per_unit_per_day'])}/unit/day",
         "icon": "🏭", "color_class": "kpi-amber"},
        {"label": "EBQ (Optimal Batch)",    "value": f"{num(e['ebq'], 0)} units",
         "icon": "✅", "color_class": "kpi-green"},
    ])

    # ── EBQ Working ───────────────────────────────────────────────────────────
    working_box("EBQ", [
        "**Formula (Module 4, slide 11):**  EBQ = √( 2 × Demand × Set-up cost ÷ Holding cost per unit )",
        f"**Given:** D = {num(d['demand_per_day'], 0)} units/day, S = {inr(d['setup_cost_per_batch'])} per batch, "
        f"C = {inr(d['holding_cost_per_unit_per_day'])} per unit per day",
        f"**Substitution:** EBQ = √( 2 × {num(d['demand_per_day'], 0)} × {num(d['setup_cost_per_batch'])} ÷ "
        f"{num(d['holding_cost_per_unit_per_day'])} ) = √( {num(e['two_d_s'])} ÷ {num(d['holding_cost_per_unit_per_day'])} ) "
        f"= √{num(e['ratio'])}",
        f"**EBQ = {num(e['ebq'], 2)} units**  → planned batch size used by CanteenOS = **{u['batch_size']} units**",
        f"**Check:** batches per day = {num(d['demand_per_day'], 0)} ÷ {num(e['ebq'], 2)} = {num(e['batches_per_period'], 2)}; "
        f"set-up cost = {num(e['batches_per_period'], 2)} × {num(d['setup_cost_per_batch'])} = {inr(e['setup_total'])}; "
        f"holding cost = (Q ÷ 2) × C = {inr(e['holding_total'])}. At the EBQ these two are equal.",
    ])

    st.info(
        f"**Interpretation:** an EBQ of about **{num(e['ebq'], 0)} units** means the cheapest batch size "
        f"for {d['name']} — the point where set-up cost and holding cost balance — is about "
        f"{num(e['ebq'], 0)} units, under the given assumptions."
    )
    if e["ebq"] > d["demand_per_day"] * 1.0001:
        st.warning("EBQ is larger than one day's demand. Hot food cannot be kept for long, so check the "
                   "shelf life before cooking a batch this big (the textbook formula ignores spoilage).")

    # ── EBQ Cost Curve ────────────────────────────────────────────────────────
    section_header("EBQ Cost Curve", "Total cost is lowest where the set-up and holding lines cross")
    sizes = list(range(max(1, int(e["ebq"] * 0.3)),
                       int(e["ebq"] * 2.2) + 2,
                       max(1, int(e["ebq"] / 25))))
    curve = pd.DataFrame({
        "Batch size":   sizes,
        "Set-up cost":  [(d["demand_per_day"] / q) * d["setup_cost_per_batch"] for q in sizes],
        "Holding cost": [(q / 2) * d["holding_cost_per_unit_per_day"] for q in sizes],
        "Total":        [cx.total_relevant_cost(q, d["demand_per_day"],
                                                d["setup_cost_per_batch"],
                                                d["holding_cost_per_unit_per_day"]) for q in sizes],
    }).set_index("Batch size")
    st.line_chart(curve)

    # ── Batch Costing ─────────────────────────────────────────────────────────
    st.markdown("---")
    section_header(f"Batch Cost at Planned Batch Size ({u['batch_size']} units)")
    n        = u["batch_size"]
    spoiled  = st.number_input("Units spoiled / burnt in the batch (optional)",
                               min_value=0, max_value=max(0, n - 1), value=0, step=1)
    abnormal = st.checkbox("Treat spoilage as abnormal loss (write the cost off to P&L)",
                           value=False,
                           help="Module 4 slide 28: normal loss is absorbed by good units; "
                                "abnormal loss goes to P&L.") if spoiled else False

    items = {
        "Direct materials":                       u["dm_unit"] * n,
        "Direct labour":                          u["dl_unit"] * n,
        "Direct expenses (packaging)":            u["de_unit"] * n,
        "Variable factory overheads (gas / fuel)": u["voh_unit"] * n,
        "Batch set-up cost":                      d["setup_cost_per_batch"],
    }
    res  = cx.batch_costing(items, n, spoiled, abnormal)
    rows = [{
        "Cost Item":   k,
        "Working":     (f"{num(v / n if k != 'Batch set-up cost' else v)} × {n}"
                        if k != "Batch set-up cost" else "per batch"),
        "Amount (₹)":  inr(v),
    } for k, v in items.items()]
    rows.append({"Cost Item": "BATCH COST", "Working": "sum of the above", "Amount (₹)": inr(res["total"])})
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

    working_box("Cost per unit", [
        f"Batch cost = {inr(res['total'])}  ·  Batch quantity = {n} units",
        f"Cost per unit = {inr(res['total'])} ÷ {n} = **{inr(res['per_unit'])}**",
        *([f"Good units = {n} − {spoiled} = {res['good_units']}; "
           + (f"abnormal loss written off to P&L = {inr(res['written_off'])}; good units stay at {inr(res['per_good_unit'])} each"
              if abnormal else
              f"cost per good unit = {inr(res['total'])} ÷ {res['good_units']} = **{inr(res['per_good_unit'])}**")]
          if spoiled else []),
    ])

    # ── Link to Component 3 ───────────────────────────────────────────────────
    st.markdown("---")
    section_header("Link to Component 3", "How EBQ feeds the Break-Even Analysis")
    st.info(
        f"Set-up cost per unit = {inr(d['setup_cost_per_batch'])} ÷ {n} = **{inr(u['setup_unit'])}**. "
        f"Adding it to material, labour, packaging and gas gives a **variable (marginal) cost of "
        f"{inr(u['variable_cost'])} per unit**, which the Break-Even page uses."
    )
