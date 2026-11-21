"""
db.py - tiny SQLite layer for CanteenOS.

Tables (kept to the minimum):
    settings     labour rate per hour
    counters     Snacks / Meals / Beverages
    ingredients  name, unit, cost per unit
    dishes       selling price, recipe yield, labour minutes, batch inputs
    recipe_bom   dish x ingredient x quantity   (the Bill of Material)
    sales        date, dish, quantity sold
    expenses     monthly fixed overheads, tagged by function (Factory/Admin/Selling/Non-operating)
    month_stock  optional opening / closing raw-material stock for the Trading A/c
"""
import os
import sqlite3
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "canteenos.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY, value REAL NOT NULL);

CREATE TABLE IF NOT EXISTS counters (
    id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE);

CREATE TABLE IF NOT EXISTS ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    unit TEXT NOT NULL,
    cost_per_unit REAL NOT NULL CHECK (cost_per_unit >= 0));

CREATE TABLE IF NOT EXISTS dishes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    counter_id INTEGER NOT NULL REFERENCES counters(id),
    selling_price REAL NOT NULL CHECK (selling_price >= 0),
    recipe_yield REAL NOT NULL CHECK (recipe_yield > 0),
    labour_minutes REAL NOT NULL CHECK (labour_minutes >= 0),
    direct_expense_per_unit REAL NOT NULL CHECK (direct_expense_per_unit >= 0),
    variable_oh_per_unit REAL NOT NULL CHECK (variable_oh_per_unit >= 0),
    setup_cost_per_batch REAL NOT NULL CHECK (setup_cost_per_batch >= 0),
    demand_per_day REAL NOT NULL CHECK (demand_per_day >= 0),
    holding_cost_per_unit_per_day REAL NOT NULL CHECK (holding_cost_per_unit_per_day > 0));

CREATE TABLE IF NOT EXISTS recipe_bom (
    dish_id INTEGER NOT NULL REFERENCES dishes(id) ON DELETE CASCADE,
    ingredient_id INTEGER NOT NULL REFERENCES ingredients(id),
    quantity_required REAL NOT NULL CHECK (quantity_required >= 0),
    PRIMARY KEY (dish_id, ingredient_id));

CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_date TEXT NOT NULL,
    dish_id INTEGER NOT NULL REFERENCES dishes(id) ON DELETE CASCADE,
    quantity_sold INTEGER NOT NULL CHECK (quantity_sold >= 0),
    UNIQUE (sale_date, dish_id));

CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    month TEXT NOT NULL,
    counter_id INTEGER REFERENCES counters(id),
    category TEXT NOT NULL,
    function TEXT NOT NULL CHECK (function IN ('Factory','Admin','Selling','Non-operating')),
    amount REAL NOT NULL CHECK (amount >= 0));

CREATE TABLE IF NOT EXISTS month_stock (
    month TEXT PRIMARY KEY,
    rm_opening REAL NOT NULL DEFAULT 0 CHECK (rm_opening >= 0),
    rm_closing REAL NOT NULL DEFAULT 0 CHECK (rm_closing >= 0));
"""


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    return conn


def df(conn, sql, params=()):
    """Run a SELECT and return a pandas DataFrame."""
    return pd.read_sql_query(sql, conn, params=params)


def one(conn, sql, params=()):
    row = conn.execute(sql, params).fetchone()
    return dict(row) if row else None


def is_empty(conn):
    return conn.execute("SELECT COUNT(*) FROM dishes").fetchone()[0] == 0


def get_setting(conn, key, default=0.0):
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return row[0] if row else default


def set_setting(conn, key, value):
    conn.execute("INSERT INTO settings(key,value) VALUES(?,?) "
                 "ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))
    conn.commit()
