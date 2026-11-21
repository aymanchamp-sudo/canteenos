"""Run with:  python -m pytest -q
Each test reproduces a worked problem from the class slides (R L Gupta decks)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import pytest
import costing as c


def close(a, b):
    return abs(a - b) < 0.005


# --- Module 3, slide 19: BOM for a bench -> Rs 1,700 -------------------------
def test_bom_bench():
    lines = [dict(name="Teak", unit="Kg", qty=10, rate=150),
             dict(name="Glue & screws", unit="Pack", qty=1, rate=50),
             dict(name="Polish", unit="Litre", qty=0.5, rate=300)]
    _, total = c.bom_cost(lines)
    assert total == 1700


# --- Module 3, slide 36: basic cost sheet ------------------------------------
def test_cost_sheet_slide36():
    rows = c.cost_sheet(1000, direct_material=450000, direct_labour=200000,
                        direct_expenses=100000, factory_oh=150000,
                        admin_oh=100000, sd_oh=75000, profit=125000)
    assert c.sheet_value(rows, "PRIME COST") == 750000
    assert c.sheet_value(rows, "FACTORY / WORKS COST") == 900000
    assert c.sheet_value(rows, "COST OF PRODUCTION") == 1000000
    assert c.sheet_value(rows, "COST OF SALES") == 1075000
    assert c.sheet_value(rows, "SALES") == 1200000


# --- Module 3, slide 39: cost sheet with adjustments -------------------------
def test_cost_sheet_slide39():
    rows = c.cost_sheet(None, with_adjustments=True, rm_opening=50000,
                        rm_purchases=500000, rm_closing=75000, freight_in=10000,
                        direct_labour=200000, direct_expenses=100000,
                        factory_oh=150000, wip_open=100000, wip_close=125000,
                        scrap=50000, admin_oh=100000, fg_open=150000,
                        fg_close=100000, sd_oh=75000, profit=150000)
    assert c.sheet_value(rows, "Direct Materials") == 485000
    assert c.sheet_value(rows, "PRIME COST") == 785000
    assert c.sheet_value(rows, "FACTORY / WORKS COST") == 860000
    assert c.sheet_value(rows, "COST OF PRODUCTION") == 960000
    assert c.sheet_value(rows, "COST OF GOODS SOLD") == 1010000
    assert c.sheet_value(rows, "COST OF SALES") == 1085000
    assert c.sheet_value(rows, "SALES") == 1235000


# --- Module 3, slide 45: overhead absorption --------------------------------
def test_absorption_slide45():
    assert c.absorption_rate(45000, 300) == 150
    assert c.absorption_rate(15000, 150) == 100
    assert c.absorbed_per_unit(150, 0.5) == 75
    assert c.absorbed_per_unit(100, 0.25) == 25


# --- Module 4, slides 10-11: batch costing and EBQ ---------------------------
def test_batch_cupcakes():
    r = c.batch_costing({"DM": 3000, "DL": 1500, "FOH": 500}, 500)
    assert r["total"] == 5000 and r["per_unit"] == 10


def test_ebq_slide11():
    r = c.ebq(10000, 400, 2)
    assert close(r["ebq"], 2000)
    assert close(r["batches_per_period"], 5)
    assert close(r["setup_total"], r["holding_total"])      # sweet spot
    assert close(r["total_relevant_cost"], 4000)


# --- Module 4, slide 41: water-bottle break-even ----------------------------
def test_bep_slide41():
    vc = 150 + 100 + 50
    r = c.bep(500, vc, 300000, actual_units=1600, target_profit=60000)
    assert r["contribution_per_unit"] == 200
    assert close(r["pv_ratio"], 0.40)
    assert close(r["bep_units"], 1500)
    assert close(r["bep_sales"], 750000)
    assert close(r["mos_units"], 100)
    assert close(r["profit"], 20000)
    assert close(r["target_units"], 1800)
    assert close(r["target_sales"], 900000)
    assert close(r["check_mos_x_pv"], r["profit"])


def test_bep_slide40():                      # BEP = 30,000 / 3,000 = 10
    r = c.bep(9000, 6000, 30000)
    assert close(r["bep_units"], 10)


def test_bep_proposal_sample():              # sample in the IA2 proposal
    r = c.bep(20, 12, 80000, actual_units=15000, target_profit=60000)
    assert close(r["bep_units"], 10000) and close(r["bep_sales"], 200000)
    assert close(r["profit"], 40000) and close(r["target_units"], 17500)


# --- Module 2, slides 16-17: Trading and P&L --------------------------------
def test_accounts_slide17():
    a = c.final_accounts(500000, rm_purchases=200000, direct_wages=60000,
                         factory_overheads=[("Factory supervisor's salary", 25000),
                                            ("Factory power & fuel", 25000)],
                         fg_opening=50000, fg_closing=45000,
                         indirect_expenses=[("Staff salaries", 100000),
                                            ("Office rent", 10000),
                                            ("Interest on loan", 25000)])
    assert a["cop"] == 310000 and a["gross_profit"] == 185000 and a["net_profit"] == 50000
    for k in ("manufacturing", "trading", "pl"):
        assert a[k]["total_dr"] == a[k]["total_cr"]


# --- Module 2, slides 12-13 --------------------------------------------------
def test_accounts_slide13():
    a = c.final_accounts(320000, rm_opening=25000, rm_purchases=140000, rm_closing=20000,
                         direct_wages=60000,
                         direct_expenses=[("Carriage inwards on RM", 3000),
                                          ("Royalty paid on production", 4000)],
                         factory_overheads=[("Factory supervisor's salary", 15000),
                                            ("Factory rent & taxes", 8000),
                                            ("Factory power & fuel", 5000),
                                            ("Depreciation on plant & machinery", 7000)],
                         fg_opening=40000, fg_closing=45000)
    assert a["cop"] == 247000 and a["gross_profit"] == 78000


# --- validation -----------------------------------------------------------------
def test_validation():
    with pytest.raises(ValueError):
        c.ebq(100, 10, 0)
    with pytest.raises(ValueError):
        c.batch_costing({"x": 1}, 0)
    with pytest.raises(ValueError):
        c.bep(-1, 0, 0)
    assert c.bep(10, 12, 1000)["bep_units"] is None      # negative contribution


# --- the Textbook Verification page must match everywhere -----------------------
def test_verification_page_all_match():
    import verification
    for p in verification.all_problems():
        for f in p["figures"]:
            assert f["match"], (p["id"], f["figure"], f["hand"], f["software"])
