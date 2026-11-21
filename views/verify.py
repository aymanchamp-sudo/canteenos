"""Textbook Verification - class problems run through the same engine as the app."""
import pandas as pd
import streamlit as st

import verification
from ui import inr, num
from theme import (
    page_header, section_header, kpi_row,
    cost_sheet_table, account_statement, verify_card_header,
)


def _fmt(f, v):
    if f["unit"] == "₹":
        return inr(v)
    return f"{num(v, 2)} {f['unit']}"


def render(conn, month):
    page_header(
        "Textbook Verification",
        "Each problem comes from the class slides (R L Gupta decks). "
        "The hand solution is written out, the same data is fed to costing.py — "
        "the engine behind every page — and the figures are compared.",
        badge="Academic",
    )

    problems = verification.all_problems()
    total    = sum(len(p["figures"]) for p in problems)
    matched  = sum(f["match"] for p in problems for f in p["figures"])

    kpi_row([
        {"label": "Problems Verified", "value": str(len(problems)),
         "icon": "📚", "color_class": "kpi-blue"},
        {"label": "Figures Checked",   "value": str(total),
         "icon": "🔢", "color_class": "kpi-indigo"},
        {"label": "Figures Matched",   "value": f"{matched} / {total}",
         "icon": "✓",  "color_class": "kpi-green" if matched == total else "kpi-red"},
        {"label": "Verification Status", "value": "PASS" if matched == total else "FAIL",
         "icon": "🏆", "color_class": "kpi-green" if matched == total else "kpi-red"},
    ])

    if matched == total:
        st.success("✅  All figures reproduced exactly — CanteenOS matches the textbook answers.")
    else:
        st.error(f"❌  {total - matched} figure(s) do not match — see below.")

    st.markdown("---")

    for p in problems:
        all_pass = all(f["match"] for f in p["figures"])

        verify_card_header(p["id"], p["title"], p["component"], all_pass, p["reference"])

        with st.expander("View full working", expanded=p.get("headline", False)):
            # Given
            section_header("Given")
            for g in p["given"]:
                st.markdown(f"- {g}")

            # Hand calculation
            section_header("Hand Calculation (Manual)")
            for h in p["hand"]:
                st.markdown(f"- {h}")

            # Software outputs
            if "bom_lines" in p:
                section_header("Software — BOM Working")
                st.dataframe(pd.DataFrame([{
                    "Item": l["name"],
                    "Qty":  f"{l['qty']} {l['unit']}",
                    "Rate": inr(l["rate"]),
                    "Cost": inr(l["cost"]),
                } for l in p["bom_lines"]]), hide_index=True, use_container_width=True)

            if "sheet" in p:
                section_header("Software — Cost Sheet")
                cost_sheet_table(p["sheet"], with_unit=p["sheet"][0]["per_unit"] is not None)

            if "accounts" in p:
                section_header("Software — Accounts (Part a)")
                account_statement("Manufacturing Account", p["accounts"]["manufacturing"])
                account_statement("Trading Account",       p["accounts"]["trading"])
                account_statement("Profit & Loss Account", p["accounts"]["pl"])

            # Comparison table
            section_header("Comparison — Hand vs Software")
            rows = [{
                "Figure":           f["figure"],
                "Hand Solution":    _fmt(f, f["hand"]),
                "Software":         _fmt(f, f["software"]),
                "Answer on Slide?": "Yes" if f["source"] == "slide" else "Worked by hand",
                "Match":            "✓" if f["match"] else "✗",
            } for f in p["figures"]]
            df = pd.DataFrame(rows)

            def style(row):
                return ["color:#065F46;font-weight:600" if row["Match"] == "✓"
                        else "color:#991B1B;font-weight:600" if col == "Match"
                        else "" for col in row.index]

            st.dataframe(df.style.apply(style, axis=1), hide_index=True, use_container_width=True)

            if p.get("note"):
                st.info(p["note"])

        st.markdown("")   # small gap between cards
