"""
services.py - the LINKING layer.

It reads the database and calls the pure formulas in costing.py.
The data flow (this is what makes the three components genuinely linked):

    ingredient price --> BOM cost --> unit cost  (Component 1)
         --> EBQ + set-up per unit               (Component 2)
         --> variable cost --> contribution --> BEP per counter (Component 3a)
    daily sales x same dish data --> Manufacturing / Trading / P&L (Component 3b)

Nothing is stored twice: change one ingredient price and every number
downstream is recomputed from it.
"""
import costing as cx
import db

FUNCTIONS = ("Factory", "Admin", "Selling")        # absorbed into dish cost
MIN_GOOD = 1


# ---------------------------------------------------------------------------
# Component 1 + 2 : per-dish unit cost, EBQ, variable cost
# ---------------------------------------------------------------------------
def dish_unit_costs(conn, dish_id):
    dish = db.one(conn, "SELECT d.*, c.name AS counter FROM dishes d "
                        "JOIN counters c ON c.id = d.counter_id WHERE d.id=?", (dish_id,))
    bom = db.df(conn, "SELECT i.id AS ingredient_id, i.name, i.unit, "
                      "b.quantity_required AS qty, i.cost_per_unit AS rate "
                      "FROM recipe_bom b JOIN ingredients i ON i.id = b.ingredient_id "
                      "WHERE b.dish_id=? ORDER BY i.name", (dish_id,))
    lines, recipe_material = cx.bom_cost(bom.to_dict("records"))
    dm_unit = recipe_material / dish["recipe_yield"]
    rate = db.get_setting(conn, "labour_rate_per_hour", 90.0)
    hours, dl_unit = cx.labour_cost(dish["labour_minutes"], rate)

    e = cx.ebq(dish["demand_per_day"], dish["setup_cost_per_batch"],
               dish["holding_cost_per_unit_per_day"])
    batch_size = max(1, round(e["ebq"])) if e["ebq"] > 0 else None
    setup_unit = (dish["setup_cost_per_batch"] / batch_size) if batch_size else 0.0

    variable = (dm_unit + dl_unit + dish["direct_expense_per_unit"]
                + dish["variable_oh_per_unit"] + setup_unit)
    return {"dish": dish, "bom_lines": lines, "recipe_material": recipe_material,
            "dm_unit": dm_unit, "labour_rate": rate, "labour_hours": hours,
            "dl_unit": dl_unit, "de_unit": dish["direct_expense_per_unit"],
            "voh_unit": dish["variable_oh_per_unit"], "ebq": e,
            "batch_size": batch_size, "setup_unit": setup_unit,
            "variable_cost": variable,
            "contribution": dish["selling_price"] - variable}


def all_dish_ids(conn):
    return [r[0] for r in conn.execute("SELECT id FROM dishes ORDER BY counter_id, id")]


def available_months(conn):
    rows = conn.execute("SELECT substr(sale_date,1,7) FROM sales UNION "
                        "SELECT month FROM expenses ORDER BY 1 DESC").fetchall()
    return [r[0] for r in rows]


def month_sales(conn, month):
    rows = conn.execute("SELECT dish_id, SUM(quantity_sold) FROM sales "
                        "WHERE substr(sale_date,1,7)=? GROUP BY dish_id", (month,)).fetchall()
    return {r[0]: r[1] for r in rows}


# ---------------------------------------------------------------------------
# Month costing : overhead absorption, cost sheets, counter BEP inputs
# ---------------------------------------------------------------------------
def month_costing(conn, month):
    qty = month_sales(conn, month)
    units = {d: dish_unit_costs(conn, d) for d in all_dish_ids(conn)}
    counters = {r["id"]: r["name"] for r in conn.execute("SELECT * FROM counters")}

    # labour hours worked per counter this month = sum(units sold x hours/unit)
    hours = {c: 0.0 for c in counters}
    for d, u in units.items():
        hours[u["dish"]["counter_id"]] += qty.get(d, 0) * u["labour_hours"]
    total_hours = sum(hours.values())

    # --- Step 1 (allocation + apportionment): overhead pool per counter & function
    exp = db.df(conn, "SELECT counter_id, category, function, amount FROM expenses "
                      "WHERE month=?", (month,))
    pools = {c: {f: 0.0 for f in FUNCTIONS} for c in counters}
    common = {f: 0.0 for f in FUNCTIONS}
    non_operating = 0.0
    for _, r in exp.iterrows():
        if r["function"] == "Non-operating":
            non_operating += r["amount"]
        elif r["counter_id"] is None or r["counter_id"] != r["counter_id"]:   # NaN = common
            common[r["function"]] += r["amount"]
        else:
            pools[int(r["counter_id"])][r["function"]] += r["amount"]
    apportioned = {c: {f: 0.0 for f in FUNCTIONS} for c in counters}
    for c in counters:
        share = (hours[c] / total_hours) if total_hours else 0.0
        for f in FUNCTIONS:
            apportioned[c][f] = common[f] * share
    # --- Step 2: absorption rate per labour hour (slide 45: rate = pool / hours)
    rates = {c: {f: cx.absorption_rate(pools[c][f] + apportioned[c][f], hours[c])
                 for f in FUNCTIONS} for c in counters}

    dishes = {}
    for d, u in units.items():
        c = u["dish"]["counter_id"]
        q = qty.get(d, 0)
        absorbed = {f: cx.absorbed_per_unit(rates[c][f], u["labour_hours"]) for f in FUNCTIONS}
        price = u["dish"]["selling_price"]
        full_cost = (u["variable_cost"] + sum(absorbed.values()))
        # cost sheet in class format (per unit when no sales this month)
        n = q if q > 0 else 1
        sheet = cx.cost_sheet(
            q if q > 0 else None,
            direct_material=u["dm_unit"] * n, direct_labour=u["dl_unit"] * n,
            direct_expenses=(u["de_unit"] + u["setup_unit"]) * n,
            factory_oh=(u["voh_unit"] + absorbed["Factory"]) * n,
            admin_oh=absorbed["Admin"] * n, sd_oh=absorbed["Selling"] * n,
            sales=price * n)
        dishes[d] = {**u, "qty": q, "absorbed": absorbed, "full_cost": full_cost,
                     "profit_per_unit": price - full_cost,
                     "profit_total": (price - full_cost) * q,
                     "sheet": sheet, "sheet_per_unit_only": q == 0}
    return {"month": month, "qty": qty, "dishes": dishes, "counters": counters,
            "hours": hours, "total_hours": total_hours, "pools": pools,
            "common": common, "apportioned": apportioned, "rates": rates,
            "non_operating": non_operating}


def counter_bep(mc, counter_id, target_profit=0.0):
    """Component 3a: break-even for one counter from the month's costing."""
    prods = [{"name": u["dish"]["name"], "price": u["dish"]["selling_price"],
              "vc": u["variable_cost"], "qty": u["qty"]}
             for u in mc["dishes"].values() if u["dish"]["counter_id"] == counter_id]
    fixed = sum(mc["pools"][counter_id].values()) + sum(mc["apportioned"][counter_id].values())
    res = cx.bep_multi(prods, fixed, target_profit)
    res["counter"] = mc["counters"][counter_id]
    return res


# ---------------------------------------------------------------------------
# Component 3b : Manufacturing, Trading and P&L for the month
# ---------------------------------------------------------------------------
def month_accounts(conn, month, mc=None):
    mc = mc or month_costing(conn, month)
    ds = mc["dishes"].values()
    sales = sum(u["qty"] * u["dish"]["selling_price"] for u in ds)
    dm = sum(u["qty"] * u["dm_unit"] for u in ds)
    wages = sum(u["qty"] * u["dl_unit"] for u in ds)
    packaging = sum(u["qty"] * u["de_unit"] for u in ds)
    setup = sum(u["qty"] * u["setup_unit"] for u in ds)
    voh = sum(u["qty"] * u["voh_unit"] for u in ds)
    contribution = sum(u["qty"] * u["contribution"] for u in ds)

    stock = db.one(conn, "SELECT rm_opening, rm_closing FROM month_stock WHERE month=?",
                   (month,)) or {"rm_opening": 0.0, "rm_closing": 0.0}
    purchases = dm + stock["rm_closing"] - stock["rm_opening"]
    problem = None
    if purchases < 0:
        problem = ("Closing stock is larger than opening stock + materials consumed, "
                   "which would make purchases negative. Please correct the stock figures.")
        purchases = 0.0

    exp = db.df(conn, "SELECT e.category, e.function, e.amount, c.name AS counter "
                      "FROM expenses e LEFT JOIN counters c ON c.id = e.counter_id "
                      "WHERE e.month=? ORDER BY e.function, e.id", (month,))

    def label(r):
        short = r["counter"].replace(" Counter", "") if isinstance(r["counter"], str) else "Common"
        return f"{r['category']} ({short})"

    factory = [(label(r), r["amount"]) for _, r in exp[exp.function == "Factory"].iterrows()]
    indirect = [(label(r), r["amount"]) for _, r in exp[exp.function.isin(["Admin", "Selling", "Non-operating"])].iterrows()]
    fixed_total = float(exp["amount"].sum())

    acc = cx.final_accounts(
        sales, rm_opening=stock["rm_opening"], rm_purchases=purchases,
        rm_closing=stock["rm_closing"], direct_wages=wages,
        direct_expenses=[("Packaging (direct expenses)", packaging),
                         ("Batch set-up costs (direct expenses)", setup)],
        factory_overheads=[("Variable factory overheads (gas / fuel)", voh)] + factory,
        indirect_expenses=indirect)
    acc.update({"stock": stock, "problem": problem, "dm": dm, "contribution": contribution,
                "fixed_total": fixed_total,
                "marginal_profit": contribution - fixed_total,
                "dish_profit_total": sum(u["profit_total"] for u in ds)})
    return acc
