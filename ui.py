"""ui.py - small display helpers shared by all pages."""
import pandas as pd
import streamlit as st


def _group_indian(int_part: str) -> str:
    """12345678 -> 1,23,45,678"""
    if len(int_part) <= 3:
        return int_part
    head, tail = int_part[:-3], int_part[-3:]
    parts = []
    while len(head) > 2:
        parts.insert(0, head[-2:])
        head = head[:-2]
    if head:
        parts.insert(0, head)
    return ",".join(parts + [tail])


def inr(x, decimals=2, sign=False):
    """Format a number as Indian rupees, e.g. 123456.5 -> Rs 1,23,456.50"""
    if x is None:
        return "-"
    neg = x < 0
    s = f"{abs(x):.{decimals}f}"
    whole, _, frac = s.partition(".")
    out = "₹" + _group_indian(whole) + ("." + frac if decimals else "")
    if neg:
        out = "-" + out
    elif sign and x > 0:
        out = "+" + out
    return out


def num(x, decimals=2):
    if x is None:
        return "-"
    s = f"{x:,.{decimals}f}"
    return s


def pct(x, decimals=2):
    return "-" if x is None else f"{x * 100:.{decimals}f}%"


def month_label(month):
    names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    y, m = month.split("-")
    return f"{names[int(m) - 1]} {y}"


def cost_sheet_table(rows, with_unit=True):
    """Show a cost sheet (list of rows from costing.cost_sheet)."""
    data = []
    for r in rows:
        label = r["label"]
        item = {"Particulars": label, "Total (₹)": inr(r["total"])}
        if with_unit:
            item["₹ / unit"] = inr(r["per_unit"]) if r["per_unit"] is not None else "-"
        data.append(item)
    df = pd.DataFrame(data)
    bold_rows = [i for i, r in enumerate(rows) if r["bold"]]

    def style(row):
        return ["font-weight:700;background-color:rgba(120,120,120,0.12)"
                if row.name in bold_rows else "" for _ in row]
    st.dataframe(df.style.apply(style, axis=1), hide_index=True, height=35 * (len(df) + 1) + 3)


def t_account(title, acc):
    """Show a T-account: debit side left, credit side right."""
    st.markdown(f"**{title}**")
    rows = [{"Particulars (Dr)": d, "Debit (₹)": inr(da) if da is not None else "",
             "Particulars (Cr)": c, "Credit (₹)": inr(ca) if ca is not None else ""}
            for d, da, c, ca in acc["rows"]]
    rows.append({"Particulars (Dr)": "Total", "Debit (₹)": inr(acc["total_dr"]),
                 "Particulars (Cr)": "Total", "Credit (₹)": inr(acc["total_cr"])})
    df = pd.DataFrame(rows)
    last = len(rows) - 1

    def style(row):
        return ["font-weight:700;background-color:rgba(120,120,120,0.12)"
                if row.name == last else "" for _ in row]
    st.dataframe(df.style.apply(style, axis=1), hide_index=True, height=35 * (len(df) + 1) + 3)


def working_box(title, lines):
    """A 'Formula / Working' panel: list of markdown lines."""
    with st.expander(f"Formula / Working - {title}", expanded=True):
        for ln in lines:
            st.markdown(ln)


def warn_if(condition, text):
    if condition:
        st.warning(text)
