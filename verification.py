"""
verification.py - the class problems used to prove the software is correct.

For each problem:
    given        the data printed on the slide
    hand         the hand-solution (typed here, with the working shown)
    software     the same data pushed through costing.py (the engine the app uses)
    comparison   figure by figure

'source' says where the hand answer comes from:
    "slide"  - the answer is printed on the class slide
    "worked" - the slide gives only the question; the answer was worked by hand here
"""
import costing as cx


def _fig(name, hand, soft, source="slide", unit="₹"):
    return {"figure": name, "hand": hand, "software": soft, "source": source,
            "unit": unit, "match": abs(hand - soft) < 0.005}


def p_bom():
    lines = [dict(name="Premium teak wood", unit="Kg", qty=10, rate=150),
             dict(name="Wood glue & screws", unit="Pack", qty=1, rate=50),
             dict(name="Wood polish", unit="Litre", qty=0.5, rate=300)]
    out, total = cx.bom_cost(lines)
    hours = 1 + 1.5 + 1.5
    labour = hours * 100
    overhead = hours * 50
    return {
        "id": "V1", "component": "Component 1", "headline": False,
        "title": "Standard cost from a Bill of Material (bench)",
        "reference": "Module 3, slides 19-21",
        "given": ["Teak wood 10 kg @ ₹150; Glue & screws 1 pack @ ₹50; Polish 0.5 litre @ ₹300",
                  "Routing: 4.0 hours of labour at ₹100/hr; overhead ₹50/hr"],
        "hand": ["Teak 10 × 150 = 1,500", "Glue 1 × 50 = 50", "Polish 0.5 × 300 = 150",
                 "Material = 1,500 + 50 + 150 = 1,700", "Labour = 4 × 100 = 400; Overhead = 4 × 50 = 200",
                 "Standard cost = 1,700 + 400 + 200 = 2,300"],
        "figures": [_fig("Standard material cost", 1700, total),
                    _fig("Standard labour cost", 400, hours * 100),
                    _fig("Standard overhead cost", 200, overhead),
                    _fig("Total standard cost", 2300, total + labour + overhead)],
        "bom_lines": out,
    }


def p_cost_sheet():
    rows = cx.cost_sheet(1000, direct_material=450000, direct_labour=200000, direct_expenses=100000,
                         factory_oh=150000, admin_oh=100000, sd_oh=75000, profit=125000)
    g = lambda k: cx.sheet_value(rows, k)
    return {
        "id": "V2", "component": "Component 1", "headline": False,
        "title": "Basic cost sheet (1,000 units)",
        "reference": "Module 3, slide 36",
        "given": ["Direct materials 4,50,000; direct labour 2,00,000; direct expenses 1,00,000",
                  "Factory OH 1,50,000; admin OH 1,00,000; selling & distribution OH 75,000; profit 1,25,000"],
        "hand": ["Prime cost = 4,50,000 + 2,00,000 + 1,00,000 = 7,50,000",
                 "Factory cost = 7,50,000 + 1,50,000 = 9,00,000",
                 "Cost of production = 9,00,000 + 1,00,000 = 10,00,000",
                 "Cost of sales = 10,00,000 + 75,000 = 10,75,000",
                 "Sales = 10,75,000 + 1,25,000 = 12,00,000"],
        "figures": [_fig("Prime cost", 750000, g("PRIME COST")),
                    _fig("Factory / works cost", 900000, g("FACTORY / WORKS COST")),
                    _fig("Cost of production", 1000000, g("COST OF PRODUCTION")),
                    _fig("Cost of sales", 1075000, g("COST OF SALES")),
                    _fig("Sales", 1200000, g("SALES")),
                    _fig("Sales per unit", 1200, g("SALES") / 1000)],
        "sheet": rows,
    }


def p_cost_sheet_adj():
    rows = cx.cost_sheet(None, with_adjustments=True, rm_opening=50000, rm_purchases=500000,
                         rm_closing=75000, freight_in=10000, direct_labour=200000,
                         direct_expenses=100000, factory_oh=150000, wip_open=100000,
                         wip_close=125000, scrap=50000, admin_oh=100000, fg_open=150000,
                         fg_close=100000, sd_oh=75000, profit=150000)
    g = lambda k: cx.sheet_value(rows, k)
    return {
        "id": "V3", "component": "Component 1", "headline": False,
        "title": "Cost sheet with stock, WIP and scrap adjustments",
        "reference": "Module 3, slide 39",
        "given": ["Opening RM 50,000; purchases 5,00,000; closing RM 75,000; freight inward 10,000",
                  "Direct labour 2,00,000; direct expenses 1,00,000; factory OH 1,50,000",
                  "Opening WIP 1,00,000; closing WIP 1,25,000; scrap 50,000; admin OH 1,00,000",
                  "Opening FG 1,50,000; closing FG 1,00,000; selling OH 75,000; profit 1,50,000"],
        "hand": ["Direct materials = 50,000 + 5,00,000 − 75,000 + 10,000 = 4,85,000",
                 "Prime cost = 4,85,000 + 2,00,000 + 1,00,000 = 7,85,000",
                 "Factory cost = 7,85,000 + 1,50,000 + 1,00,000 − 1,25,000 − 50,000 = 8,60,000",
                 "Cost of production = 8,60,000 + 1,00,000 = 9,60,000",
                 "COGS = 9,60,000 + 1,50,000 − 1,00,000 = 10,10,000",
                 "Cost of sales = 10,10,000 + 75,000 = 10,85,000; Sales = 10,85,000 + 1,50,000 = 12,35,000"],
        "figures": [_fig("Direct materials", 485000, g("Direct Materials")),
                    _fig("Prime cost", 785000, g("PRIME COST")),
                    _fig("Factory / works cost", 860000, g("FACTORY / WORKS COST")),
                    _fig("Cost of production", 960000, g("COST OF PRODUCTION")),
                    _fig("Cost of goods sold", 1010000, g("COST OF GOODS SOLD")),
                    _fig("Cost of sales", 1085000, g("COST OF SALES")),
                    _fig("Sales", 1235000, g("SALES"))],
        "sheet": rows,
    }


def p_batch_ebq():
    batch = cx.batch_costing({"Direct materials": 3000, "Direct labour": 1500,
                              "Factory overheads": 500}, 500)
    burnt = cx.batch_costing({"Direct materials": 3000, "Direct labour": 1500,
                              "Factory overheads": 500}, 500, spoiled_units=50)
    e = cx.ebq(10000, 400, 2)
    return {
        "id": "V4", "component": "Component 2", "headline": True,
        "title": "TEXTBOOK PROBLEM 1 - Batch costing and Economic Batch Quantity",
        "reference": "Module 4, slides 10-11 (Bakery cupcakes; EBQ exercise)",
        "given": ["Bakery batch of 500 cupcakes: direct materials ₹3,000; direct labour ₹1,500; factory overheads ₹500",
                  "EBQ exercise: annual demand 10,000 units; set-up cost ₹400 per batch; holding cost ₹2 per unit per year"],
        "hand": ["Batch cost = 3,000 + 1,500 + 500 = ₹5,000;  cost per cupcake = 5,000 ÷ 500 = ₹10",
                 "If 50 cupcakes are burnt and absorbed by the good units: 5,000 ÷ 450 = ₹11.11 per good cupcake "
                 "(the slide asks this; its answer is not printed - see note)",
                 "EBQ = √(2 × 10,000 × 400 ÷ 2) = √4,000,000 = 2,000 units",
                 "Batches per year = 10,000 ÷ 2,000 = 5;  set-up cost = 5 × 400 = ₹2,000;  holding cost = (2,000 ÷ 2) × 2 = ₹2,000"],
        "figures": [_fig("Batch cost", 5000, batch["total"]),
                    _fig("Cost per cupcake", 10, batch["per_unit"]),
                    _fig("Cost per good cupcake after 50 burnt (absorbed)", 5000 / 450, burnt["per_good_unit"], "worked"),
                    _fig("EBQ", 2000, e["ebq"], "worked", "units"),
                    _fig("Batches per year", 5, e["batches_per_period"], "worked", "batches"),
                    _fig("Annual set-up cost", 2000, e["setup_total"], "worked"),
                    _fig("Annual holding cost", 2000, e["holding_total"], "worked")],
        "note": "The burnt-cupcake question can be answered two ways. If the loss is treated as normal and absorbed by good "
                "units the cost is ₹11.11; if treated as abnormal (slide 28) the good units stay at ₹10 and ₹500 goes to "
                "the P&L. CanteenOS offers both on the Batch page - confirm the convention your professor expects.",
    }


def p_bep():
    vc = 150 + 100 + 50
    r = cx.bep(500, vc, 300000, actual_units=1600, target_profit=60000)
    return {
        "id": "V5", "component": "Component 3", "headline": True,
        "title": "TEXTBOOK PROBLEM 2 - Marginal costing and Break-Even Analysis (steel water bottles)",
        "reference": "Module 4, slide 41 (also slide 40)",
        "given": ["Selling price ₹500; direct material ₹150; direct labour ₹100; variable overhead ₹50 per unit",
                  "Fixed costs ₹3,00,000 per month; normal capacity 2,000 units; actual 1,600 units",
                  "Target net profit ₹60,000"],
        "hand": ["Marginal cost per unit = 150 + 100 + 50 = ₹300",
                 "Contribution per unit = 500 − 300 = ₹200;  P/V ratio = 200 ÷ 500 = 40%",
                 "BEP units = 3,00,000 ÷ 200 = 1,500;  BEP sales = 1,500 × 500 = ₹7,50,000",
                 "Margin of safety = 1,600 − 1,500 = 100 units (₹50,000)",
                 "Profit at 1,600 units = 1,600 × 200 − 3,00,000 = ₹20,000",
                 "Target units = (3,00,000 + 60,000) ÷ 200 = 1,800;  revenue = 1,800 × 500 = ₹9,00,000"],
        "figures": [_fig("Marginal cost per unit", 300, vc),
                    _fig("Contribution per unit", 200, r["contribution_per_unit"], "worked"),
                    _fig("P/V ratio (%)", 40, r["pv_ratio"] * 100, "worked", "%"),
                    _fig("BEP (units)", 1500, r["bep_units"], "worked", "units"),
                    _fig("BEP (sales ₹)", 750000, r["bep_sales"], "worked"),
                    _fig("Margin of safety (units)", 100, r["mos_units"], "worked", "units"),
                    _fig("Profit at 1,600 units", 20000, r["profit"], "worked"),
                    _fig("Units for target profit ₹60,000", 1800, r["target_units"], "worked", "units"),
                    _fig("Revenue for target profit", 900000, r["target_sales"], "worked")],
        "note": "Slide 41 prints the question; its answers are on a picture slide that could not be read, so the hand "
                "solution above was worked out independently. Slide 40 (BEP = 30,000 ÷ 3,000 = 10) is also checked in the tests.",
    }


def p_accounts():
    a = cx.final_accounts(
        500000, rm_purchases=200000, direct_wages=60000,
        factory_overheads=[("Factory supervisor's salary", 25000), ("Factory power & fuel", 25000)],
        fg_opening=50000, fg_closing=45000,
        indirect_expenses=[("Staff salaries", 100000), ("Office rent", 10000), ("Interest on loan", 25000)])
    b = cx.final_accounts(
        320000, rm_opening=25000, rm_purchases=140000, rm_closing=20000, direct_wages=60000,
        direct_expenses=[("Carriage inwards on raw materials", 3000), ("Royalty paid on production", 4000)],
        factory_overheads=[("Factory supervisor's salary", 15000), ("Factory rent & taxes", 8000),
                           ("Factory power & fuel", 5000), ("Depreciation on plant & machinery", 7000)],
        fg_opening=40000, fg_closing=45000)
    return {
        "id": "V6", "component": "Component 3", "headline": False,
        "title": "Manufacturing, Trading and Profit & Loss Account",
        "reference": "Module 2, slides 12-13 and 16-17",
        "given": ["(a) Sales 5,00,000; RM purchases 2,00,000; direct wages 60,000; supervisor 25,000; power & fuel 25,000; "
                  "Op. FG 50,000; Cl. FG 45,000; staff salaries 1,00,000; office rent 10,000; interest 25,000",
                  "(b) Alpha Manufacturing: sales 3,20,000; Op/Cl RM 25,000/20,000; purchases 1,40,000; wages 60,000; "
                  "other factory items; Op/Cl FG 40,000/45,000"],
        "hand": ["(a) CoP = 2,00,000 + 60,000 + 25,000 + 25,000 = 3,10,000",
                 "    COGS = 3,10,000 + 50,000 − 45,000 = 3,15,000;  Gross profit = 5,00,000 − 3,15,000 = 1,85,000",
                 "    Net profit = 1,85,000 − (1,00,000 + 10,000 + 25,000) = 50,000",
                 "(b) RM consumed = 25,000 + 1,40,000 − 20,000 = 1,45,000; CoP = 1,45,000 + 60,000 + 15,000 + 8,000 + 5,000 + 3,000 + 7,000 + 4,000 = 2,47,000",
                 "    COGS = 2,47,000 + 40,000 − 45,000 = 2,42,000;  Gross profit = 3,20,000 − 2,42,000 = 78,000"],
        "figures": [_fig("(a) Cost of production", 310000, a["cop"]),
                    _fig("(a) Gross profit", 185000, a["gross_profit"]),
                    _fig("(a) Net profit", 50000, a["net_profit"]),
                    _fig("(b) Cost of production", 247000, b["cop"]),
                    _fig("(b) Gross profit", 78000, b["gross_profit"])],
        "accounts": a,
    }


def all_problems():
    return [p_bom(), p_cost_sheet(), p_cost_sheet_adj(), p_batch_ebq(), p_bep(), p_accounts()]
