"""Component 1 : Recipe BOM -> standard cost -> Cost Sheet (Module 3)."""
import pandas as pd
import streamlit as st

import db
import services as sv
from ui import inr, num, month_label
from theme import (
    page_header, section_header, working_box, cost_sheet_table, status_badge,
)


def render(conn, month):
    page_header(
        "Recipe & BOM → Cost Sheet",
        "Component 1 · Module 3 · Standard cost from the Bill of Material, "
        "then the cost sheet in the class format (Prime → Factory → Production → Sales).",
        badge="Component 1",
    )

    _ingredient_prices(conn)
    st.markdown("---")

    dishes = db.df(conn, "SELECT d.id, d.name, c.name AS counter FROM dishes d "
                         "JOIN counters c ON c.id=d.counter_id ORDER BY d.counter_id, d.id")
    if dishes.empty:
        st.info("No dishes yet. Add one below.")
        _new_dish(conn)
        return

    labels = {int(r.id): f"{r.name}  ({r.counter})" for r in dishes.itertuples()}

    section_header("Select Dish")
    dish_id = st.selectbox("Dish", list(labels), format_func=labels.get,
                           label_visibility="collapsed")

    tab_edit, tab_sheet = st.tabs(["✏️  Edit Dish & BOM", "📋  Cost Sheet (with working)"])
    with tab_edit:
        _edit_dish(conn, dish_id)
        st.markdown("---")
        _edit_bom(conn, dish_id)
        st.markdown("---")
        _new_dish(conn)
    with tab_sheet:
        _cost_sheet(conn, dish_id, month)


# ---------------------------------------------------------------------------
def _ingredient_prices(conn):
    section_header("Ingredient Prices",
                   "Change a price here and every cost sheet, EBQ, BEP and monthly account recalculates — "
                   "this is the integration demo.")
    ing = db.df(conn, "SELECT id, name, unit, cost_per_unit FROM ingredients ORDER BY name")
    edited = st.data_editor(
        ing, hide_index=True, key="ing_editor", disabled=["id", "name", "unit"],
        column_config={
            "id":            None,
            "name":          "Ingredient",
            "unit":          "Unit",
            "cost_per_unit": st.column_config.NumberColumn(
                "Cost per unit (₹)", min_value=0.0, format="%.2f"),
        },
        use_container_width=True,
    )
    if st.button("💾  Save ingredient prices", type="primary"):
        bad = edited["cost_per_unit"].isna() | (edited["cost_per_unit"] < 0)
        if bad.any():
            st.error("Cost per unit cannot be negative or blank.")
        else:
            for r in edited.itertuples():
                conn.execute("UPDATE ingredients SET cost_per_unit=? WHERE id=?",
                             (float(r.cost_per_unit), int(r.id)))
            conn.commit()
            st.toast("Prices saved ✓")
            st.rerun()

    with st.expander("➕  Add a new ingredient"):
        with st.form("new_ing", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            name = c1.text_input("Name")
            unit = c2.text_input("Unit (kg, litre, pc …)")
            cost = c3.number_input("Cost per unit (₹)", min_value=0.0, step=1.0)
            if st.form_submit_button("Add ingredient"):
                if not name.strip() or not unit.strip():
                    st.error("Name and unit are required.")
                elif db.one(conn, "SELECT id FROM ingredients WHERE lower(name)=lower(?)", (name.strip(),)):
                    st.error("That ingredient already exists.")
                else:
                    conn.execute("INSERT INTO ingredients(name,unit,cost_per_unit) VALUES(?,?,?)",
                                 (name.strip(), unit.strip(), cost))
                    conn.commit()
                    st.rerun()


def _edit_dish(conn, dish_id):
    d = db.one(conn, "SELECT * FROM dishes WHERE id=?", (dish_id,))
    section_header(f"Dish Details — {d['name']}")
    with st.form(f"dish_{dish_id}"):
        c1, c2, c3 = st.columns(3)
        price = c1.number_input("Selling price per unit (₹)", min_value=0.0,
                                value=float(d["selling_price"]), step=1.0)
        yld   = c2.number_input("Recipe yield (units one BOM makes)", min_value=1.0,
                                value=float(d["recipe_yield"]), step=1.0)
        mins  = c3.number_input("Labour minutes per unit", min_value=0.0,
                                value=float(d["labour_minutes"]), step=0.5)
        c4, c5 = st.columns(2)
        de  = c4.number_input("Direct expense per unit — packaging (₹)", min_value=0.0,
                              value=float(d["direct_expense_per_unit"]), step=0.1)
        voh = c5.number_input("Variable factory overhead per unit — gas/fuel (₹)", min_value=0.0,
                              value=float(d["variable_oh_per_unit"]), step=0.1)
        if st.form_submit_button("💾  Save dish details", type="primary"):
            conn.execute("UPDATE dishes SET selling_price=?, recipe_yield=?, labour_minutes=?, "
                         "direct_expense_per_unit=?, variable_oh_per_unit=? WHERE id=?",
                         (price, yld, mins, de, voh, dish_id))
            conn.commit()
            st.toast("Dish saved ✓")
            st.rerun()

    rate = db.get_setting(conn, "labour_rate_per_hour", 90.0)
    new_rate = st.number_input("Labour rate per hour for all dishes (₹)", min_value=0.0,
                               value=float(rate), step=5.0)
    if new_rate != rate:
        db.set_setting(conn, "labour_rate_per_hour", new_rate)
        st.rerun()


def _edit_bom(conn, dish_id):
    section_header("Bill of Material", "Quantities per recipe run")
    bom = db.df(conn, "SELECT i.id AS ingredient_id, i.name, i.unit, b.quantity_required AS qty, "
                      "i.cost_per_unit AS rate FROM recipe_bom b JOIN ingredients i ON i.id=b.ingredient_id "
                      "WHERE b.dish_id=? ORDER BY i.name", (dish_id,))
    edited = st.data_editor(
        bom, hide_index=True, key=f"bom_{dish_id}", disabled=["ingredient_id", "name", "unit", "rate"],
        column_config={
            "ingredient_id": None,
            "name":          "Ingredient",
            "unit":          "Unit",
            "qty":           st.column_config.NumberColumn("Quantity required", min_value=0.0, format="%.3f"),
            "rate":          st.column_config.NumberColumn("Rate (₹, edit above)", format="%.2f"),
        },
        use_container_width=True,
    )
    if st.button("💾  Save quantities", key=f"saveq_{dish_id}", type="primary"):
        if (edited["qty"].isna() | (edited["qty"] < 0)).any():
            st.error("Quantity cannot be negative or blank.")
        else:
            for r in edited.itertuples():
                conn.execute("UPDATE recipe_bom SET quantity_required=? WHERE dish_id=? AND ingredient_id=?",
                             (float(r.qty), dish_id, int(r.ingredient_id)))
            conn.commit()
            st.toast("Quantities saved ✓")
            st.rerun()

    with st.expander("Add / Remove an ingredient line"):
        ing  = db.df(conn, "SELECT id, name, unit FROM ingredients ORDER BY name")
        used = set(bom["ingredient_id"])
        free = ing[~ing["id"].isin(used)]
        with st.form(f"addline_{dish_id}", clear_on_submit=True):
            a, b = st.columns(2)
            pick = a.selectbox(
                "Ingredient", list(free["id"]),
                format_func=lambda i: f"{free.set_index('id').loc[i, 'name']} ({free.set_index('id').loc[i, 'unit']})"
            ) if len(free) else None
            q = b.number_input("Quantity", min_value=0.0, step=0.1)
            if st.form_submit_button("Add line") and pick is not None:
                conn.execute("INSERT INTO recipe_bom VALUES(?,?,?)", (dish_id, int(pick), q))
                conn.commit()
                st.rerun()
        if len(bom):
            rm = st.selectbox(
                "Remove line", list(bom["ingredient_id"]),
                format_func=lambda i: bom.set_index("ingredient_id").loc[i, "name"],
                key=f"rm_{dish_id}",
            )
            if st.button("Remove selected ingredient", key=f"rmb_{dish_id}"):
                conn.execute("DELETE FROM recipe_bom WHERE dish_id=? AND ingredient_id=?",
                             (dish_id, int(rm)))
                conn.commit()
                st.rerun()


def _new_dish(conn):
    counters = db.df(conn, "SELECT id, name FROM counters")
    with st.expander("➕  Add a new dish"):
        with st.form("new_dish", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            name  = c1.text_input("Dish name")
            ctr   = c2.selectbox("Counter", list(counters["id"]),
                                 format_func=lambda i: counters.set_index("id").loc[i, "name"])
            price = c3.number_input("Selling price (₹)", min_value=0.0, step=1.0)
            c4, c5, c6 = st.columns(3)
            yld   = c4.number_input("Recipe yield (units)", min_value=1.0, value=10.0)
            mins  = c5.number_input("Labour minutes per unit", min_value=0.0, value=1.0)
            setup = c6.number_input("Set-up cost per batch (₹)", min_value=0.0, value=50.0)
            c7, c8 = st.columns(2)
            demand = c7.number_input("Demand per day (units)", min_value=0.0, value=50.0)
            hold   = c8.number_input("Holding cost per unit per day (₹)", min_value=0.01, value=1.0)
            if st.form_submit_button("Create dish (then add its BOM above)"):
                if not name.strip():
                    st.error("Dish name is required.")
                elif db.one(conn, "SELECT id FROM dishes WHERE lower(name)=lower(?)", (name.strip(),)):
                    st.error("A dish with this name already exists.")
                else:
                    conn.execute(
                        "INSERT INTO dishes(name,counter_id,selling_price,recipe_yield,labour_minutes,"
                        "direct_expense_per_unit,variable_oh_per_unit,setup_cost_per_batch,"
                        "demand_per_day,holding_cost_per_unit_per_day) VALUES(?,?,?,?,?,?,?,?,?,?)",
                        (name.strip(), int(ctr), price, yld, mins, 0, 0, setup, demand, hold),
                    )
                    conn.commit()
                    st.rerun()


# ---------------------------------------------------------------------------
def _cost_sheet(conn, dish_id, month):
    mc = sv.month_costing(conn, month)
    u  = mc["dishes"][dish_id]
    d  = u["dish"]

    # ── Recipe Details & Cost Summary 2-Column Overview ───────────────────────
    c_left, c_right = st.columns(2, gap="medium")
    with c_left:
        section_header("Recipe Details", f"Specifications for {d['name']}")
        st.dataframe(pd.DataFrame([
            {"Parameter": "Dish Name",          "Value": d["name"]},
            {"Parameter": "Counter",            "Value": d["counter"]},
            {"Parameter": "Selling Price",      "Value": inr(d["selling_price"])},
            {"Parameter": "Batch Yield",        "Value": f"{num(d['recipe_yield'], 0)} units"},
            {"Parameter": "Labour Time",        "Value": f"{num(d['labour_minutes'], 1)} min / unit"},
        ]), hide_index=True, use_container_width=True)

    with c_right:
        section_header("Unit Cost Summary", "Standard unit cost buildup")
        st.dataframe(pd.DataFrame([
            {"Cost Element": "Direct Material / unit",       "Amount": inr(u["dm_unit"])},
            {"Cost Element": "Direct Labour / unit",         "Amount": inr(u["dl_unit"])},
            {"Cost Element": "Packaging & Setup / unit",     "Amount": inr(u["de_unit"] + u["setup_unit"])},
            {"Cost Element": "Variable Cost / unit",         "Amount": inr(u["variable_cost"])},
            {"Cost Element": "Full Cost of Sales / unit",    "Amount": inr(u["full_cost"])},
        ]), hide_index=True, use_container_width=True)

    st.markdown("---")

    if not len(u["bom_lines"]):
        st.warning("This dish has no BOM yet — add ingredients on the 'Edit Dish & BOM' tab.")

    # ── Step 1 : BOM → direct material ───────────────────────────────────────
    section_header("Step 1 · Standard Material Cost from BOM",
                   "Quantity × Rate = Cost for each ingredient")
    bom_df = pd.DataFrame([{
        "Ingredient":        l["name"],
        "Quantity":          f"{num(l['qty'], 3)} {l['unit']}",
        "Rate (₹)":          num(l["rate"]),
        "Qty × Rate":        f"{num(l['qty'], 3)} × {num(l['rate'])}",
        "Cost (₹)":          inr(l["cost"]),
    } for l in u["bom_lines"]])
    if len(bom_df):
        st.dataframe(bom_df, hide_index=True, use_container_width=True)

    working_box("Direct material per unit", [
        f"Material cost of one recipe run = **{inr(u['recipe_material'])}**",
        f"Recipe yield = **{num(d['recipe_yield'], 0)} units**",
        f"Direct material per unit = {inr(u['recipe_material'])} ÷ {num(d['recipe_yield'], 0)} = **{inr(u['dm_unit'])}**",
        f"Direct labour per unit = {num(d['labour_minutes'])} min ÷ 60 × ₹{num(u['labour_rate'])}/hr "
        f"= {num(u['labour_hours'], 4)} hr × ₹{num(u['labour_rate'])} = **{inr(u['dl_unit'])}**",
        f"Direct expenses per unit = packaging {inr(u['de_unit'])} + batch set-up {inr(d['setup_cost_per_batch'])} ÷ "
        f"EBQ {u['batch_size']} (from Component 2) = {inr(u['de_unit'])} + {inr(u['setup_unit'])} "
        f"= **{inr(u['de_unit'] + u['setup_unit'])}**",
    ])

    # ── Step 2 : overhead absorption ─────────────────────────────────────────
    section_header(
        f"Step 2 · Fixed Overheads Absorbed — {month_label(month)}",
        "OAR = Overheads ÷ Labour hours; Absorbed per unit = OAR × hours per unit",
    )
    c = d["counter_id"]
    rate_rows = []
    for f in sv.FUNCTIONS:
        pool = mc["pools"][c][f] + mc["apportioned"][c][f]
        rate_rows.append({
            "Overhead":               f"{f} overheads",
            "Counter pool (₹)":       inr(pool, 0),
            "Counter labour hrs":     num(mc["hours"][c], 1),
            "Rate per hour (₹)":      num(mc["rates"][c][f]),
            "Hours per unit":         num(u["labour_hours"], 4),
            "Absorbed per unit (₹)":  inr(u["absorbed"][f]),
        })
    st.dataframe(pd.DataFrame(rate_rows), hide_index=True, use_container_width=True)
    st.caption("Counter pool = overheads allocated directly to the counter + a share of common overheads "
               "(manager, hall rent) apportioned on labour hours. Interest is non-operating and not absorbed.")

    # ── Step 3 : class-format cost sheet ─────────────────────────────────────
    qty = u["qty"]
    if qty:
        section_header(f"Step 3 · Cost Sheet — {month_label(month)}",
                       f"{num(qty, 0)} units sold")
    else:
        section_header("Step 3 · Cost Sheet (per unit)",
                       "No sales this month — totals show one unit; fixed overheads cannot be absorbed.")

    cost_sheet_table(u["sheet"])

    # Result banner
    if u["profit_per_unit"] < 0:
        st.error(
            f"**{d['name']} loses {inr(-u['profit_per_unit'])} per unit once overheads are absorbed** "
            f"(cost of sales {inr(u['full_cost'])} vs price {inr(d['selling_price'])}). "
            f"It still earns a contribution of {inr(u['contribution'])} per unit, "
            "so it helps pay the fixed costs — dropping it would reduce total profit."
        )
    else:
        st.success(f"✅  {d['name']} earns **{inr(u['profit_per_unit'])} per unit** after absorbing all overheads.")
