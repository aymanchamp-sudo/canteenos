"""Component 3b : monthly Manufacturing, Trading and Profit & Loss Account (Module 2)."""
import pandas as pd
import streamlit as st

import db
import services as sv
from ui import inr, pct, month_label
from theme import (
    page_header, section_header, kpi_row, working_box,
    account_statement, check_row,
)


def render(conn, month):
    page_header(
        "Monthly Trading & Profit & Loss Account",
        f"Component 3 · Module 2 · {month_label(month)} · "
        "built from the daily sales, the same BOM costs and the monthly overheads.",
        badge="Component 3",
    )

    _overheads(conn, month)
    mc = sv.month_costing(conn, month)
    if not mc["qty"]:
        st.info("No sales recorded for this month.")
        return

    # Raw-material stock (optional)
    stock = db.one(conn, "SELECT rm_opening, rm_closing FROM month_stock WHERE month=?", (month,)) \
        or {"rm_opening": 0.0, "rm_closing": 0.0}
    with st.expander("📦  Raw-material stock (optional — default nil because food is cooked fresh daily)"):
        with st.form("stock_form"):
            a, b = st.columns(2)
            op = a.number_input("Opening stock of raw materials (₹)",
                                min_value=0.0, value=float(stock["rm_opening"]), step=500.0)
            cl = b.number_input("Closing stock of raw materials (₹)",
                                min_value=0.0, value=float(stock["rm_closing"]), step=500.0)
            if st.form_submit_button("💾  Save stock", type="primary"):
                conn.execute(
                    "INSERT INTO month_stock(month,rm_opening,rm_closing) VALUES(?,?,?) "
                    "ON CONFLICT(month) DO UPDATE SET rm_opening=excluded.rm_opening, "
                    "rm_closing=excluded.rm_closing",
                    (month, op, cl),
                )
                conn.commit()
                st.rerun()
        st.caption("Purchases = materials consumed (units sold × BOM cost) + closing stock − opening stock.")

    acc = sv.month_accounts(conn, month, mc)
    if acc["problem"]:
        st.error(acc["problem"])

    # ── KPI Row ───────────────────────────────────────────────────────────────
    kpi_row([
        {"label": "Sales",              "value": inr(acc["sales"], 0),
         "icon": "💰", "color_class": "kpi-blue"},
        {"label": "Cost of Production", "value": inr(acc["cop"], 0),
         "icon": "📦", "color_class": "kpi-indigo"},
        {"label": "Gross Profit",       "value": inr(acc["gross_profit"], 0),
         "sub": pct(acc["gross_profit"] / acc["sales"]) if acc["sales"] else "—",
         "icon": "📈", "color_class": "kpi-green"},
        {"label": "Net Profit",         "value": inr(acc["net_profit"], 0),
         "sub": pct(acc["net_profit"] / acc["sales"]) if acc["sales"] else "—",
         "icon": "✅", "color_class": "kpi-green" if acc["net_profit"] >= 0 else "kpi-red"},
    ])

    st.markdown("---")

    # ── 1 · Sales Summary ─────────────────────────────────────────────────────
    section_header("1 · Sales Summary")
    rows = [{
        "Dish":      u["dish"]["name"],
        "Units":     f"{u['qty']:,}",
        "Price":     inr(u["dish"]["selling_price"]),
        "Sales (₹)": inr(u["qty"] * u["dish"]["selling_price"], 0),
    } for u in mc["dishes"].values()]
    rows.append({
        "Dish":      "TOTAL",
        "Units":     f"{sum(u['qty'] for u in mc['dishes'].values()):,}",
        "Price":     "",
        "Sales (₹)": inr(acc["sales"], 0),
    })
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

    st.markdown("---")

    # ── 2 · Manufacturing Account ──────────────────────────────────────────────
    section_header("2 · Manufacturing Account",
                   "Debit: cost inputs · Credit: cost of production transferred")
    account_statement(f"Manufacturing Account for {month_label(month)}", acc["manufacturing"],
                      caption_text="Opening RM + Purchases + Direct wages + Direct expenses + Factory overheads "
                                   "− Closing RM = Cost of Production")

    # ── 3 · Trading Account ───────────────────────────────────────────────────
    section_header("3 · Trading Account",
                   "Debit: cost of goods sold · Credit: sales revenue")
    account_statement(f"Trading Account for {month_label(month)}", acc["trading"],
                      caption_text="Sales − Cost of Goods Sold (= Cost of Production + Opening FG − Closing FG) "
                                   f"= Gross Profit {inr(acc['gross_profit'], 0)}")

    # ── 4 · Profit & Loss Account ─────────────────────────────────────────────
    section_header("4 · Profit & Loss Account",
                   "Gross profit adjusted for indirect expenses → Net Profit")
    account_statement(f"Profit & Loss Account for {month_label(month)}", acc["pl"],
                      caption_text=f"Gross Profit + Indirect income − Indirect expenses = "
                                   f"Net Profit {inr(acc['net_profit'], 0)}")

    # ── Working box ───────────────────────────────────────────────────────────
    working_box("Accounts", [
        "**Manufacturing A/c:** Opening RM + Purchases + Direct wages + Direct expenses + Factory overheads − Closing RM "
        f"= Cost of Production = **{inr(acc['cop'])}**",
        f"**Trading A/c:** Sales − (Cost of Production + Opening FG − Closing FG) = {inr(acc['sales'])} − {inr(acc['cogs'])} "
        f"= **Gross Profit {inr(acc['gross_profit'])}**",
        "**P&L A/c:** Net Profit = Gross Profit + Indirect income − Indirect expenses "
        f"= **{inr(acc['net_profit'])}**",
        "Finished-goods stock is nil: food is prepared and sold the same day.",
        "Where the figures come from: direct material = Σ(units sold × BOM cost per unit); wages = Σ(units × labour per unit); "
        "packaging, gas and batch set-up likewise per unit; fixed overheads come from the expenses table by function "
        "(Factory → Manufacturing A/c; Admin, Selling and Non-operating → P&L).",
    ], expanded=False)

    st.markdown("---")

    # ── 5 · Consistency Checks ────────────────────────────────────────────────
    section_header("5 · Consistency Checks",
                   "Marginal costing reconciliation — both methods must agree because there is no closing stock.")
    ok1 = abs(acc["net_profit"] - acc["marginal_profit"]) < 0.01
    ok2 = abs(acc["dish_profit_total"] - mc["non_operating"] - acc["net_profit"]) < 0.01

    check_row(
        ok1,
        f"Marginal costing vs financial accounts: "
        f"total contribution {inr(acc['contribution'], 0)} − "
        f"fixed costs {inr(acc['fixed_total'], 0)} = {inr(acc['marginal_profit'], 0)}  ·  "
        f"Net profit in P&L = {inr(acc['net_profit'], 0)}",
    )
    check_row(
        ok2,
        f"Cost sheets vs financial accounts: "
        f"sum of dish profits after absorption {inr(acc['dish_profit_total'], 0)} − "
        f"non-operating expenses {inr(mc['non_operating'], 0)} = "
        f"{inr(acc['dish_profit_total'] - mc['non_operating'], 0)}  ·  "
        f"Net profit = {inr(acc['net_profit'], 0)}",
    )
    st.caption("The two profits agree because there is no closing stock (all food is sold the same day), "
               "so no fixed cost is carried forward.")


# ---------------------------------------------------------------------------
FUNCTION_HELP = ("Factory → Manufacturing A/c and absorbed into dish cost; Admin and Selling → P&L and absorbed; "
                 "Non-operating (interest etc.) → P&L only.")


def _overheads(conn, month):
    """View / edit the month's fixed overheads (the 'expenses' table)."""
    exp = db.df(conn,
                "SELECT e.id, COALESCE(c.name,'Common') AS counter, e.category, e.function, e.amount "
                "FROM expenses e LEFT JOIN counters c ON c.id=e.counter_id WHERE e.month=? ORDER BY e.id",
                (month,))
    with st.expander(f"⚙️  Monthly Fixed Overheads — {month_label(month)} (view / edit)",
                     expanded=exp.empty):
        if exp.empty:
            st.warning("No overheads recorded for this month.")
            other = db.one(conn,
                           "SELECT month FROM expenses WHERE month<>? ORDER BY month DESC LIMIT 1",
                           (month,))
            if other and st.button(f"Copy overheads from {month_label(other['month'])}"):
                conn.execute(
                    "INSERT INTO expenses(month,counter_id,category,function,amount) "
                    "SELECT ?,counter_id,category,function,amount FROM expenses WHERE month=?",
                    (month, other["month"]),
                )
                conn.commit()
                st.rerun()
        else:
            edited = st.data_editor(
                exp, hide_index=True, key=f"exp_{month}",
                disabled=["id", "counter", "category", "function"],
                column_config={
                    "id":       None,
                    "counter":  "Counter",
                    "category": "Expense",
                    "function": "Function",
                    "amount":   st.column_config.NumberColumn("Amount (₹)", min_value=0.0, format="%.0f"),
                },
                use_container_width=True,
            )
            if st.button("💾  Save overhead amounts", key=f"saveexp_{month}", type="primary"):
                if (edited["amount"].isna() | (edited["amount"] < 0)).any():
                    st.error("Amounts cannot be negative or blank.")
                else:
                    for r in edited.itertuples():
                        conn.execute("UPDATE expenses SET amount=? WHERE id=?",
                                     (float(r.amount), int(r.id)))
                    conn.commit()
                    st.rerun()

        st.caption(FUNCTION_HELP)
        counters = db.df(conn, "SELECT id, name FROM counters")
        with st.form(f"addexp_{month}", clear_on_submit=True):
            a, b, c, d = st.columns(4)
            ctr = a.selectbox("Counter", [0] + list(counters["id"]),
                              format_func=lambda i: "Common (shared)" if i == 0
                              else counters.set_index("id").loc[i, "name"])
            cat = b.text_input("Expense name")
            fn  = c.selectbox("Function", ["Factory", "Admin", "Selling", "Non-operating"])
            amt = d.number_input("Amount (₹)", min_value=0.0, step=500.0)
            if st.form_submit_button("Add overhead"):
                if not cat.strip():
                    st.error("Expense name is required.")
                else:
                    conn.execute(
                        "INSERT INTO expenses(month,counter_id,category,function,amount) VALUES(?,?,?,?,?)",
                        (month, None if ctr == 0 else int(ctr), cat.strip(), fn, amt),
                    )
                    conn.commit()
                    st.rerun()
