"""
seed.py - fills the database with realistic SAMPLE canteen data.
(Illustrative figures for the demo - not textbook figures.)

Run once:   python seed.py          (app.py also calls it if the DB is empty)
Reset:      python seed.py --reset
"""
import os
import random
import sys
from datetime import date, timedelta

import db

COUNTERS = ["Snacks Counter", "Meals Counter", "Beverages Counter"]

# name, unit, cost per unit (Rs)
INGREDIENTS = [
    ("Potato", "kg", 30), ("Maida (flour)", "kg", 40), ("Cooking oil", "litre", 140),
    ("Spices & masala", "kg", 300), ("Green peas", "kg", 80), ("Pav (bun)", "pc", 4),
    ("Besan", "kg", 90), ("Green chilli", "kg", 80), ("Rice", "kg", 60),
    ("Dal", "kg", 120), ("Atta", "kg", 40), ("Mixed vegetables", "kg", 50),
    ("Curd", "litre", 60), ("Chickpeas", "kg", 110), ("Onion & tomato", "kg", 40),
    ("Milk", "litre", 56), ("Tea leaves", "kg", 400), ("Sugar", "kg", 45),
    ("Ginger", "kg", 120), ("Coffee powder", "kg", 1200), ("Ice cream", "litre", 250),
]

# dish: counter, price, yield, labour minutes/unit, direct exp/unit (packaging),
#       variable OH/unit (gas), set-up Rs/batch, demand/day, holding cost/unit/day, BOM
DISHES = {
    "Samosa": ("Snacks Counter", 15, 50, 1.0, 0.40, 0.60, 90, 120, 1.50,
               {"Potato": 3, "Maida (flour)": 1.5, "Cooking oil": 1.2,
                "Spices & masala": 0.2, "Green peas": 0.5}),
    "Vada Pav": ("Snacks Counter", 20, 40, 1.2, 0.50, 0.60, 80, 80, 1.00,
                 {"Potato": 2.4, "Besan": 0.6, "Cooking oil": 0.8, "Spices & masala": 0.1,
                  "Pav (bun)": 40, "Green chilli": 0.2}),
    "Veg Thali": ("Meals Counter", 70, 20, 6.0, 2.00, 3.00, 150, 100, 2.00,
                  {"Rice": 2, "Dal": 1.5, "Atta": 2, "Mixed vegetables": 4,
                   "Cooking oil": 0.6, "Spices & masala": 0.1, "Curd": 2}),
    "Chole Bhature": ("Meals Counter", 60, 25, 4.0, 1.50, 2.50, 120, 60, 1.50,
                      {"Chickpeas": 2.5, "Maida (flour)": 2.5, "Cooking oil": 1.5,
                       "Spices & masala": 0.15, "Onion & tomato": 2, "Curd": 0.5}),
    "Masala Chai": ("Beverages Counter", 12, 50, 0.5, 0.60, 0.80, 50, 300, 0.50,
                    {"Milk": 3, "Tea leaves": 0.2, "Sugar": 1.2, "Ginger": 0.15}),
    "Cold Coffee": ("Beverages Counter", 40, 20, 2.0, 2.00, 0.50, 60, 80, 1.00,
                    {"Milk": 3, "Coffee powder": 0.06, "Sugar": 0.3, "Ice cream": 0.6}),
}

# monthly FIXED overheads: counter (None = common), category, function, amount
EXPENSES = [
    ("Snacks Counter", "Cook supervisor salary", "Factory", 10000),
    ("Snacks Counter", "Fryer & equipment depreciation", "Factory", 2500),
    ("Snacks Counter", "Electricity", "Factory", 3000),
    ("Snacks Counter", "Counter staff salary", "Selling", 8000),
    ("Meals Counter", "Cook supervisor salary", "Factory", 14000),
    ("Meals Counter", "Equipment depreciation", "Factory", 3500),
    ("Meals Counter", "Electricity", "Factory", 4500),
    ("Meals Counter", "Counter staff salary", "Selling", 12000),
    ("Beverages Counter", "Supervisor salary", "Factory", 5000),
    ("Beverages Counter", "Machine depreciation", "Factory", 1500),
    ("Beverages Counter", "Electricity", "Factory", 2000),
    ("Beverages Counter", "Counter staff salary", "Selling", 6000),
    (None, "Canteen hall rent", "Factory", 12000),
    (None, "Canteen manager salary", "Admin", 20000),
    (None, "Licence, hygiene & accounts", "Admin", 4000),
    (None, "Interest on bank loan", "Non-operating", 3000),
]

DAYS_CLOSED = {6}          # Sunday (Monday = 0)


def month_days(year, month, last_day=None):
    d = date(year, month, 1)
    out = []
    while d.month == month and (last_day is None or d.day <= last_day):
        out.append(d)
        d += timedelta(days=1)
    return out


def seed(conn):
    cur = conn.cursor()
    db.set_setting(conn, "labour_rate_per_hour", 90.0)

    for name in COUNTERS:
        cur.execute("INSERT INTO counters(name) VALUES(?)", (name,))
    counter_id = {r["name"]: r["id"] for r in conn.execute("SELECT * FROM counters")}

    for name, unit, rate in INGREDIENTS:
        cur.execute("INSERT INTO ingredients(name,unit,cost_per_unit) VALUES(?,?,?)",
                    (name, unit, rate))
    ing_id = {r["name"]: r["id"] for r in conn.execute("SELECT * FROM ingredients")}

    for name, (ctr, price, yld, mins, de, voh, setup, dem, hold, bom) in DISHES.items():
        cur.execute(
            "INSERT INTO dishes(name,counter_id,selling_price,recipe_yield,labour_minutes,"
            "direct_expense_per_unit,variable_oh_per_unit,setup_cost_per_batch,"
            "demand_per_day,holding_cost_per_unit_per_day) VALUES(?,?,?,?,?,?,?,?,?,?)",
            (name, counter_id[ctr], price, yld, mins, de, voh, setup, dem, hold))
        dish_id = cur.lastrowid
        for ing, qty in bom.items():
            cur.execute("INSERT INTO recipe_bom VALUES(?,?,?)", (dish_id, ing_id[ing], qty))
    dish_id = {r["name"]: r["id"] for r in conn.execute("SELECT * FROM dishes")}

    # Expenses: September and October 2026 (two full months)
    for month in ("2026-09", "2026-10"):
        for ctr, cat, func, amt in EXPENSES:
            cur.execute("INSERT INTO expenses(month,counter_id,category,function,amount) "
                        "VALUES(?,?,?,?,?)",
                        (month, counter_id.get(ctr) if ctr else None, cat, func, amt))

    # Daily sales: demand per day with weekday pattern + random noise (fixed seed)
    rng = random.Random(2026)
    weekday_factor = {0: 1.05, 1: 1.0, 2: 1.0, 3: 1.02, 4: 0.9, 5: 0.7}
    for d in month_days(2026, 9) + month_days(2026, 10):
        if d.weekday() in DAYS_CLOSED:
            continue
        for name, spec in DISHES.items():
            base = spec[7] * weekday_factor[d.weekday()]
            qty = max(0, round(rng.gauss(base, base * 0.06)))
            cur.execute("INSERT INTO sales(sale_date,dish_id,quantity_sold) VALUES(?,?,?)",
                        (d.isoformat(), dish_id[name], qty))
    conn.commit()


def reset_and_seed():
    if os.path.exists(db.DB_PATH):
        os.remove(db.DB_PATH)
    conn = db.get_conn()
    seed(conn)
    return conn


if __name__ == "__main__":
    if "--reset" in sys.argv or not os.path.exists(db.DB_PATH):
        reset_and_seed()
        print("Database created with sample data:", db.DB_PATH)
    else:
        conn = db.get_conn()
        if db.is_empty(conn):
            seed(conn)
            print("Database seeded.")
        else:
            print("Database already has data. Use --reset to rebuild it.")
