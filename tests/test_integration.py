"""Integration: an ingredient price change must flow all the way to the P&L."""
import os, sys, shutil, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import db, seed, services as sv


def fresh_conn(tmp):
    db.DB_PATH = os.path.join(tmp, "t.db")
    return seed.reset_and_seed()


def test_potato_price_flows_downstream():
    with tempfile.TemporaryDirectory() as tmp:
        conn = fresh_conn(tmp)
        month = "2026-10"
        before = sv.month_accounts(conn, month)
        mc0 = sv.month_costing(conn, month)
        samosa = next(i for i, u in mc0["dishes"].items() if u["dish"]["name"] == "Samosa")
        vc0 = mc0["dishes"][samosa]["variable_cost"]
        qty = mc0["dishes"][samosa]["qty"]

        conn.execute("UPDATE ingredients SET cost_per_unit=40 WHERE name='Potato'")
        conn.commit()
        mc1 = sv.month_costing(conn, month)
        after = sv.month_accounts(conn, month, mc1)

        # samosa: +10 x 3 kg / 50 = +0.60 per unit
        assert abs(mc1["dishes"][samosa]["variable_cost"] - vc0 - 0.60) < 1e-9
        # vada pav also uses potato (2.4 kg / 40 units) -> total profit drops
        drop = before["net_profit"] - after["net_profit"]
        assert drop > 0
        # both consistency checks still hold
        assert abs(after["net_profit"] - after["marginal_profit"]) < 0.01
        assert abs(after["dish_profit_total"] - mc1["non_operating"] - after["net_profit"]) < 0.01
        for k in ("manufacturing", "trading", "pl"):
            assert abs(after[k]["total_dr"] - after[k]["total_cr"]) < 0.01


def test_ebq_changes_setup_per_unit():
    with tempfile.TemporaryDirectory() as tmp:
        conn = fresh_conn(tmp)
        did = conn.execute("SELECT id FROM dishes WHERE name='Samosa'").fetchone()[0]
        a = sv.dish_unit_costs(conn, did)
        conn.execute("UPDATE dishes SET setup_cost_per_batch=360 WHERE id=?", (did,))   # 4x -> EBQ x2
        conn.commit()
        b = sv.dish_unit_costs(conn, did)
        assert abs(b["ebq"]["ebq"] - 2 * a["ebq"]["ebq"]) < 1e-6
        assert b["variable_cost"] != a["variable_cost"]
