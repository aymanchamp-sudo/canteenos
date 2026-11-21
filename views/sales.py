"""Daily sales entry. Amount = quantity × the dish's current selling price."""
from datetime import date

import pandas as pd
import streamlit as st

import db
import services as sv
from ui import inr, month_label
from theme import page_header, section_header, kpi_row


def render(conn, month):
    page_header(
        "Daily Sales",
        "Sales use the same dishes and prices as the cost sheets — the amount is calculated, never typed.",
    )

    dishes = db.df(conn, "SELECT id, name, selling_price FROM dishes ORDER BY counter_id, id")
    info   = dishes.set_index("id")

    # ── Entry form ────────────────────────────────────────────────────────────
    section_header("Record a Sale")
    with st.form("sale_form", clear_on_submit=False):
        c1, c2, c3 = st.columns(3)
        year, mon   = (int(x) for x in month.split("-"))
        sale_date   = c1.date_input("Date", value=date(year, mon, 1))
        dish_id     = c2.selectbox("Dish", list(info.index),
                                   format_func=lambda i: info.loc[i, "name"])
        qty         = c3.number_input("Quantity sold", min_value=0, value=0, step=1)
        st.caption("Amount = quantity × selling price. Saving a date + dish that already exists replaces it.")
        if st.form_submit_button("💾  Save sale", type="primary"):
            if qty < 0:
                st.error("Quantity cannot be negative.")
            else:
                conn.execute(
                    "INSERT INTO sales(sale_date,dish_id,quantity_sold) VALUES(?,?,?) "
                    "ON CONFLICT(sale_date,dish_id) DO UPDATE SET quantity_sold=excluded.quantity_sold",
                    (sale_date.isoformat(), int(dish_id), int(qty)),
                )
                conn.commit()
                amount = qty * info.loc[dish_id, "selling_price"]
                st.success(f"Saved: {qty} × {inr(info.loc[dish_id, 'selling_price'])} = **{inr(amount)}**")
                if sale_date > date.today():
                    st.warning("This date is in the future.")

    # ── Monthly summary ───────────────────────────────────────────────────────
    sales = db.df(conn,
                  "SELECT s.id, s.sale_date AS Date, d.name AS Dish, s.quantity_sold AS Qty, "
                  "d.selling_price AS Price FROM sales s JOIN dishes d ON d.id=s.dish_id "
                  "WHERE substr(s.sale_date,1,7)=? ORDER BY s.sale_date, d.id",
                  (month,))
    if sales.empty:
        st.info("No sales for this month yet.")
        return

    sales["Amount"] = sales["Qty"] * sales["Price"]

    # KPIs
    total_units  = int(sales["Qty"].sum())
    total_sales  = sales["Amount"].sum()
    num_days     = sales["Date"].nunique()
    avg_per_day  = total_sales / num_days if num_days else 0

    kpi_row([
        {"label": "Total Units Sold",    "value": f"{total_units:,}",      "icon": "🍽️", "color_class": "kpi-blue"},
        {"label": "Total Sales",         "value": inr(total_sales, 0),     "icon": "💰", "color_class": "kpi-green"},
        {"label": "Days with Sales",     "value": str(num_days),           "icon": "📅", "color_class": "kpi-indigo"},
        {"label": "Avg Sales / Day",     "value": inr(avg_per_day, 0),     "icon": "📈", "color_class": "kpi-profit"},
    ])

    # ── Monthly summary table ─────────────────────────────────────────────────
    st.markdown("---")
    section_header(f"Monthly Sales Summary — {month_label(month)}",
                   "Daily quantities accumulated")
    qty_map = sv.month_sales(conn, month)
    summary_rows = []
    for _, r in dishes.iterrows():
        u = qty_map.get(r["id"], 0)
        s = u * r["selling_price"]
        summary_rows.append({
            "Dish":      r["name"],
            "Price":     inr(r["selling_price"]),
            "Units":     f"{u:,}",
            "Sales":     inr(s, 0),
        })
    total_u = sum(qty_map.get(r["id"], 0) for _, r in dishes.iterrows())
    total_s = sum(qty_map.get(r["id"], 0) * r["selling_price"] for _, r in dishes.iterrows())
    summary_rows.append({
        "Dish":      "TOTAL",
        "Price":     "—",
        "Units":     f"{total_u:,}",
        "Sales":     inr(total_s, 0),
    })
    st.dataframe(pd.DataFrame(summary_rows), hide_index=True, use_container_width=True)

    # ── Daily quantities pivot ────────────────────────────────────────────────
    section_header("Daily Quantities", "Pivot of quantity sold per dish per day")
    pivot = sales.pivot(index="Date", columns="Dish", values="Qty").fillna(0).astype(int)
    st.dataframe(pivot, use_container_width=True)

    # ── Daily sales bar chart ─────────────────────────────────────────────────
    section_header("Daily Sales (₹)", "Total revenue by date")
    st.bar_chart(sales.groupby("Date")["Amount"].sum())

    # ── Delete entry ──────────────────────────────────────────────────────────
    st.markdown("---")
    with st.expander("🗑️  Delete an entry"):
        label = {int(r.id): f"{r.Date} · {r.Dish} · {r.Qty}" for r in sales.itertuples()}
        pick  = st.selectbox("Entry to delete", list(label), format_func=label.get)
        if st.button("Delete selected entry"):
            conn.execute("DELETE FROM sales WHERE id=?", (pick,))
            conn.commit()
            st.rerun()
