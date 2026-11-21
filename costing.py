"""
costing.py - the accounting engine of CanteenOS.

Every formula in the project lives in this one file. It has NO database and
NO Streamlit code, so the same functions are used by:
    * the app pages (live canteen data), and
    * the Textbook Verification page (class problems).
That is how we prove the software reproduces the textbook answers.

Formulas follow the class slides (Module 2, 3 and 4, R L Gupta deck).
"""
from math import sqrt


# ----------------------------------------------------------------------------
# COMPONENT 1 : Recipe BOM -> standard cost -> cost sheet   (Module 3)
# ----------------------------------------------------------------------------

def bom_cost(lines):
    """Standard material cost from a Bill of Material (Module 3, slide 19).

    lines : list of dicts with keys name, unit, qty, rate
    Each line:  Standard Material Cost = Quantity x Rate
    Returns (lines_with_cost, total_material_cost)
    """
    out, total = [], 0.0
    for ln in lines:
        if ln["qty"] < 0 or ln["rate"] < 0:
            raise ValueError("Quantity and rate cannot be negative")
        cost = ln["qty"] * ln["rate"]
        out.append({**ln, "cost": cost})
        total += cost
    return out, total


def labour_cost(minutes_per_unit, rate_per_hour):
    """Direct labour per unit = labour time (hours) x labour rate per hour
    (Module 3, slide 20 - routing: Labour Time x Labour Rate)."""
    hours = minutes_per_unit / 60.0
    return hours, hours * rate_per_hour


def cost_sheet(qty=None, *, direct_material=0.0,
               rm_opening=0.0, rm_purchases=0.0, rm_closing=0.0, freight_in=0.0,
               direct_labour=0.0, direct_expenses=0.0,
               factory_oh=0.0, wip_open=0.0, wip_close=0.0, scrap=0.0,
               admin_oh=0.0, fg_open=0.0, fg_close=0.0, sd_oh=0.0,
               profit=None, sales=None, with_adjustments=False):
    """Cost sheet in the class format (Module 3, slides 36, 38, 39).

        Direct Material + Direct Labour + Direct Expenses = PRIME COST
        + Factory Overheads                               = FACTORY / WORKS COST
        + Administration Overheads                        = COST OF PRODUCTION
        + Selling & Distribution Overheads                = COST OF SALES
        + Profit                                          = SALES

    with_adjustments=True uses the slide-39 version where direct material is
    built from opening stock + purchases - closing stock + freight inward,
    factory cost adjusts for WIP and scrap, and COGS adjusts for finished goods.

    qty (units produced) is optional; if given, a per-unit column is returned.
    Returns a list of rows: dict(label, total, per_unit, bold).
    """
    rows = []

    def add(label, total, bold=False):
        pu = (total / qty) if qty else None
        rows.append({"label": label, "total": total, "per_unit": pu, "bold": bold})

    if with_adjustments:
        add("Opening stock of raw material", rm_opening)
        add("Add: Purchases of raw material", rm_purchases)
        add("Less: Closing stock of raw material", -rm_closing)
        add("Add: Freight inward", freight_in)
        dm = rm_opening + rm_purchases - rm_closing + freight_in
        add("Direct Materials", dm, bold=True)
    else:
        dm = direct_material
        add("Direct Materials", dm)

    add("Direct Labour", direct_labour)
    add("Direct Expenses", direct_expenses)
    prime = dm + direct_labour + direct_expenses
    add("PRIME COST", prime, bold=True)

    add("Add: Factory Overheads", factory_oh)
    factory = prime + factory_oh
    if with_adjustments:
        add("Add: Opening WIP", wip_open)
        add("Less: Closing WIP", -wip_close)
        add("Less: Sale of scrap", -scrap)
        factory += wip_open - wip_close - scrap
    add("FACTORY / WORKS COST", factory, bold=True)

    add("Add: Administration Overheads", admin_oh)
    cop = factory + admin_oh
    add("COST OF PRODUCTION", cop, bold=True)

    cogs = cop
    if with_adjustments:
        add("Add: Opening finished goods", fg_open)
        add("Less: Closing finished goods", -fg_close)
        cogs = cop + fg_open - fg_close
        add("COST OF GOODS SOLD", cogs, bold=True)

    add("Add: Selling & Distribution Overheads", sd_oh)
    cos = cogs + sd_oh
    add("COST OF SALES", cos, bold=True)

    if sales is not None and profit is None:
        profit = sales - cos
    if profit is None:
        profit = 0.0
    add("Add: Profit" if profit >= 0 else "Less: Loss", profit)
    add("SALES", cos + profit, bold=True)
    return rows


def sheet_value(rows, label):
    """Pick one figure out of a cost-sheet row list by its label."""
    for r in rows:
        if r["label"] == label:
            return r["total"]
    raise KeyError(label)


# ----------------------------------------------------------------------------
# Overhead absorption (Module 3, slides 44-45)
# ----------------------------------------------------------------------------

def absorption_rate(overhead_pool, total_hours):
    """Overhead Absorption Rate = Overheads / Labour hours  (slide 45, step 4)."""
    if total_hours <= 0:
        return 0.0
    return overhead_pool / total_hours


def absorbed_per_unit(rate_per_hour, hours_per_unit):
    """Absorbed overhead per unit = OAR x hours per unit   (slide 45, step 5)."""
    return rate_per_hour * hours_per_unit


# ----------------------------------------------------------------------------
# COMPONENT 2 : Batch costing and EBQ   (Module 4, slides 9-11)
# ----------------------------------------------------------------------------

def batch_costing(cost_items, batch_qty, spoiled_units=0, abnormal=False):
    """Batch costing (slide 10 - Bakery / cupcakes).

    Batch cost = sum of the cost items (direct material, labour, overheads ...)
    Cost per unit = Batch cost / Batch quantity.

    If some units are spoiled in the batch there are two conventions:
      * absorbed (normal) : cost per GOOD unit = Batch cost / good units
      * abnormal          : good units stay at Batch cost / Batch qty and the
                            cost of the spoiled units is written off to P&L
                            (Module 4, slide 28: abnormal loss -> P&L).
    """
    if batch_qty <= 0:
        raise ValueError("Batch quantity must be greater than zero")
    if spoiled_units < 0 or spoiled_units >= batch_qty:
        raise ValueError("Spoiled units must be between 0 and batch quantity")
    total = sum(cost_items.values())
    per_unit = total / batch_qty
    good = batch_qty - spoiled_units
    if spoiled_units == 0:
        return {"total": total, "per_unit": per_unit, "good_units": good,
                "per_good_unit": per_unit, "written_off": 0.0}
    if abnormal:
        return {"total": total, "per_unit": per_unit, "good_units": good,
                "per_good_unit": per_unit, "written_off": spoiled_units * per_unit}
    return {"total": total, "per_unit": per_unit, "good_units": good,
            "per_good_unit": total / good, "written_off": 0.0}


def ebq(demand, setup_cost, holding_cost):
    """Economic Batch Quantity (Module 4, slide 11).

        EBQ = sqrt( 2 x Demand x Set-up cost per batch / Holding cost per unit )

    Demand and holding cost must use the SAME time period (the slide uses a
    year; the canteen uses a day because food is perishable).

    At EBQ, total set-up cost = total holding cost (the 'sweet spot').
    """
    if demand < 0 or setup_cost < 0:
        raise ValueError("Demand and set-up cost cannot be negative")
    if holding_cost <= 0:
        raise ValueError("Holding cost per unit must be greater than zero")
    two_d_s = 2 * demand * setup_cost
    ratio = two_d_s / holding_cost
    q = sqrt(ratio)
    batches = demand / q if q > 0 else 0.0
    setup_total = batches * setup_cost
    holding_total = (q / 2) * holding_cost       # average stock = Q / 2
    return {"ebq": q, "two_d_s": two_d_s, "ratio": ratio,
            "batches_per_period": batches,
            "setup_total": setup_total, "holding_total": holding_total,
            "total_relevant_cost": setup_total + holding_total}


def total_relevant_cost(batch_size, demand, setup_cost, holding_cost):
    """Set-up cost + holding cost for any batch size (used for the EBQ curve)."""
    if batch_size <= 0:
        return None
    return (demand / batch_size) * setup_cost + (batch_size / 2) * holding_cost


# ----------------------------------------------------------------------------
# COMPONENT 3a : Marginal costing and break-even   (Module 4, slides 36-41)
# ----------------------------------------------------------------------------

def bep(price, variable_cost, fixed_cost, actual_units=None, target_profit=0.0):
    """Marginal costing / break-even for ONE product.

        Contribution per unit = Selling price - Variable (marginal) cost
        P/V ratio             = Contribution / Selling price
        BEP (units)           = Fixed cost / Contribution per unit
        BEP (Rs)              = Fixed cost / P/V ratio   (= BEP units x price)
        Margin of safety      = Actual sales - BEP sales
        Profit                = Contribution - Fixed cost
        Target units          = (Fixed cost + Target profit) / Contribution per unit
    """
    if price < 0 or variable_cost < 0 or fixed_cost < 0:
        raise ValueError("Price, variable cost and fixed cost cannot be negative")
    c = price - variable_cost
    out = {"contribution_per_unit": c,
           "pv_ratio": (c / price) if price > 0 else 0.0,
           "feasible": c > 0}
    if c <= 0:                                   # cannot break even
        out.update(bep_units=None, bep_sales=None)
        return out
    out["bep_units"] = fixed_cost / c
    out["bep_sales"] = fixed_cost / out["pv_ratio"]
    out["target_units"] = (fixed_cost + target_profit) / c
    out["target_sales"] = out["target_units"] * price
    if actual_units is not None:
        out["actual_units"] = actual_units
        out["total_contribution"] = c * actual_units
        out["profit"] = c * actual_units - fixed_cost
        out["mos_units"] = actual_units - out["bep_units"]
        out["mos_sales"] = out["mos_units"] * price
        sales = actual_units * price
        out["mos_pct"] = (out["mos_sales"] / sales) if sales else 0.0
        out["check_mos_x_pv"] = out["mos_sales"] * out["pv_ratio"]   # equals profit
    return out


def bep_multi(products, fixed_cost, target_profit=0.0):
    """Break-even for a COUNTER selling several dishes (sales-mix method).

    products : list of dicts  name, price, vc, qty   (qty = actual units sold)
    Composite P/V = Total contribution / Total sales
    BEP sales     = Fixed cost / Composite P/V
    Each dish's share of the BEP follows the actual sales mix.
    """
    if fixed_cost < 0:
        raise ValueError("Fixed cost cannot be negative")
    sales = sum(p["price"] * p["qty"] for p in products)
    contrib = sum((p["price"] - p["vc"]) * p["qty"] for p in products)
    out = {"total_sales": sales, "total_contribution": contrib,
           "fixed_cost": fixed_cost, "profit": contrib - fixed_cost}
    if sales <= 0 or contrib <= 0:
        out.update(pv_ratio=(contrib / sales) if sales else 0.0, bep_sales=None,
                   mos_sales=None, mos_pct=None, rows=[], feasible=False)
        return out
    pv = contrib / sales
    out["pv_ratio"] = pv
    out["feasible"] = True
    out["bep_sales"] = fixed_cost / pv
    out["mos_sales"] = sales - out["bep_sales"]
    out["mos_pct"] = out["mos_sales"] / sales
    out["target_sales"] = (fixed_cost + target_profit) / pv
    rows = []
    for p in products:
        share = (p["price"] * p["qty"]) / sales
        bep_rs = out["bep_sales"] * share
        rows.append({"name": p["name"], "price": p["price"], "vc": p["vc"],
                     "contribution": p["price"] - p["vc"],
                     "pv_ratio": (p["price"] - p["vc"]) / p["price"] if p["price"] else 0,
                     "qty": p["qty"], "sales": p["price"] * p["qty"],
                     "mix_pct": share,
                     "bep_sales": bep_rs,
                     "bep_units": bep_rs / p["price"] if p["price"] else 0})
    out["rows"] = rows
    return out


# ----------------------------------------------------------------------------
# COMPONENT 3b : Manufacturing, Trading and Profit & Loss   (Module 2, slides 5-17)
# ----------------------------------------------------------------------------

def final_accounts(sales, *, rm_opening=0.0, rm_purchases=0.0, rm_closing=0.0,
                   direct_wages=0.0, direct_expenses=None, factory_overheads=None,
                   fg_opening=0.0, fg_closing=0.0, fg_purchases=0.0,
                   indirect_expenses=None, indirect_income=None):
    """Manufacturing Account, Trading Account and Profit & Loss Account.

    Manufacturing A/c  : Op. RM + Purchases + Direct wages + Direct expenses
                         + Factory overheads - Cl. RM = Cost of Production
    Trading A/c        : Sales vs (CoP + Op. FG + FG purchases - Cl. FG) = Gross Profit
    P&L A/c            : Gross Profit + Indirect income - Indirect expenses = Net Profit

    direct_expenses / factory_overheads / indirect_* : lists of (label, amount)
    Returns the three accounts as T-account rows plus the key totals.
    """
    direct_expenses = direct_expenses or []
    factory_overheads = factory_overheads or []
    indirect_expenses = indirect_expenses or []
    indirect_income = indirect_income or []

    # --- Manufacturing account ---
    mfg_dr = [("To Opening stock of raw materials", rm_opening),
              ("To Raw material purchases", rm_purchases),
              ("To Direct wages", direct_wages)]
    mfg_dr += [("To " + n, a) for n, a in direct_expenses]
    mfg_dr += [("To " + n, a) for n, a in factory_overheads]
    mfg_total = sum(a for _, a in mfg_dr)
    cop = mfg_total - rm_closing
    mfg_cr = [("By Closing stock of raw materials", rm_closing),
              ("By Cost of production c/f", cop)]

    # --- Trading account ---
    tr_dr = [("To Cost of production b/f", cop),
             ("To Opening stock of finished goods", fg_opening),
             ("To Finished goods purchases", fg_purchases)]
    tr_cr = [("By Sales", sales),
             ("By Closing stock of finished goods", fg_closing)]
    cogs = cop + fg_opening + fg_purchases - fg_closing
    gross = sales - cogs
    if gross >= 0:
        tr_dr.append(("To Gross profit c/f", gross))
    else:
        tr_cr.append(("By Gross loss c/f", -gross))

    # --- Profit & loss account ---
    pl_dr = [("To " + n, a) for n, a in indirect_expenses]
    pl_cr = []
    if gross >= 0:
        pl_cr.append(("By Gross profit b/f", gross))
    else:
        pl_dr.append(("To Gross loss b/f", -gross))
    pl_cr += [("By " + n, a) for n, a in indirect_income]
    net = gross + sum(a for _, a in indirect_income) - sum(a for _, a in indirect_expenses)
    if net >= 0:
        pl_dr.append(("To Net profit", net))
    else:
        pl_cr.append(("By Net loss", -net))

    return {"cop": cop, "cogs": cogs, "gross_profit": gross, "net_profit": net,
            "sales": sales,
            "manufacturing": _t_account(mfg_dr, mfg_cr),
            "trading": _t_account(tr_dr, tr_cr),
            "pl": _t_account(pl_dr, pl_cr)}


def _t_account(dr, cr):
    """Pair debit and credit lines side by side and add the equal totals."""
    n = max(len(dr), len(cr))
    dr = dr + [("", None)] * (n - len(dr))
    cr = cr + [("", None)] * (n - len(cr))
    rows = [(d[0], d[1], c[0], c[1]) for d, c in zip(dr, cr)]
    total_dr = sum(a for _, a in dr if a is not None)
    total_cr = sum(a for _, a in cr if a is not None)
    return {"rows": rows, "total_dr": total_dr, "total_cr": total_cr}
