# CanteenOS - College Canteen Costing & Financial Management

FCA IA2 · Topic A11 · Modules 2 + 3 + 4 · Python + Streamlit + SQLite

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py
```

The database (`canteenos.db`) is created automatically with sample data on first run.
To reset the demo data: delete `canteenos.db` (or run `python seed.py --reset`).
To run the checks: `python -m pytest -q`

## The pipeline (three linked components)

```
Component 1  Recipe BOM -> standard material cost -> cost sheet per dish        (Module 3)
Component 2  Unit cost -> batch cost -> EBQ -> set-up cost per unit              (Module 4)
Component 3  Variable cost -> contribution -> P/V -> BEP per counter             (Module 4)
             Daily sales -> Manufacturing A/c -> Trading A/c -> P&L              (Module 2)
```

Nothing is typed twice. Change a potato price and the cost sheet, variable cost, BEP, monthly
accounts and dashboard all change.

## Files

| File | Purpose |
|---|---|
| `costing.py` | ALL accounting formulas. No database, no UI. Used by the app and by the verification page |
| `services.py` | Reads the database and calls `costing.py` - this is where the components are linked |
| `verification.py` | The class problems with hand solutions, run through `costing.py` |
| `db.py`, `seed.py` | SQLite schema and sample data |
| `app.py`, `views/`, `ui.py` | Streamlit pages |
| `tests/` | Unit tests (class problems), integration test (price change), page smoke test |

## Formulas and where they come from (class slides)

| Formula | Slide |
|---|---|
| Standard material cost = Quantity × Rate (BOM) | Module 3, slide 19 |
| Cost sheet: Prime → Factory/Works → Cost of Production → Cost of Sales → Sales | Module 3, slides 36, 38, 39 |
| Overhead absorption rate = Overheads ÷ Labour hours; absorbed per unit = Rate × hours per unit | Module 3, slides 44-45 |
| Batch cost per unit = Batch cost ÷ Batch quantity | Module 4, slide 10 |
| EBQ = √(2 × Demand × Set-up cost ÷ Holding cost per unit) | Module 4, slide 11 |
| Contribution = Sales − Variable cost; BEP = Fixed cost ÷ Contribution per unit; Margin of safety = Actual − BEP | Module 4, slides 38-41 |
| Manufacturing A/c → Cost of Production; Trading A/c → Gross Profit; P&L → Net Profit | Module 2, slides 5-17 |

## Textbook (class) problems reproduced - page "Textbook Verification"

* **Problem 1 - Batch costing + EBQ:** slides 10-11 (cupcakes ₹5,000/500 = ₹10; EBQ for D = 10,000, S = ₹400, C = ₹2 → 2,000 units)
* **Problem 2 - Marginal costing + BEP:** slide 41 (water bottles; BEP 1,500 units / ₹7,50,000)
* Also reproduced: BOM bench (slide 19-21), cost sheets (slides 36 and 39), Trading & P&L (slides 12-13, 16-17)

Slide 41's printed answers are on a picture that could not be read, so its hand solution was worked
independently and is labelled "Worked by hand" on the page. Compare with your class notes.

## Design decisions (ours, not from the slides) - be ready to explain

1. **Set-up cost per unit at EBQ is part of variable cost** (it grows with the number of batches). This is how Component 2 feeds Component 3.
2. **EBQ uses a day, not a year**, because food is perishable (the formula only needs consistent units). A warning shows if EBQ exceeds one day's demand.
3. **BEP per counter uses the sales-mix method** (composite P/V = total contribution ÷ total sales).
4. **Fixed overheads are absorbed on labour hours** (the method on slide 45). Common overheads (manager, hall rent) are apportioned to counters on labour hours first. A different basis would change which dishes "lose money".
5. **No finished-goods stock** (food sold the same day). Raw-material stock defaults to nil; purchases are derived as consumed + closing − opening.
6. **Variable costs go to the Manufacturing/Trading account; fixed costs by function** (Factory → Manufacturing A/c, Admin/Selling/Non-operating → P&L).
7. **Burnt/spoiled units:** both conventions (absorbed by good units vs abnormal loss to P&L) are offered. Confirm which your professor expects.
8. Cost-sheet function names (Factory / Admin / Selling) follow slide 36.

## Built-in self-checks (Monthly Trading & P&L page)

* Contribution − fixed costs (marginal costing) **=** Net profit in the P&L
* Sum of dish profits after absorption − non-operating expenses **=** Net profit in the P&L

Both hold because there is no closing stock.

## 10-minute demo script

1. Dashboard: show the pipeline line and the "dishes that lose money" warning.
2. Recipe & BOM → Cost Sheet (Samosa): BOM lines, per-unit working, absorption table, cost sheet.
3. Batch Costing & EBQ (Samosa): formula, substitution, interpretation, curve.
4. Break-Even (Snacks Counter): contribution table, composite P/V, BEP, margin of safety.
5. Daily Sales → Monthly Trading & P&L: T-accounts and the two consistency checks.
6. **Live integration:** raise Potato from ₹30 to ₹40 → watch Samosa's cost, BEP and net profit change.
7. Textbook Verification: every figure ✓.

## AI-use declaration (required by the IA2 brief)

Claude (Anthropic) was used to help design the architecture and write the code. All formulas were taken from the
class slides and verified against the textbook problems on the Verification page. Every group member should be able to
explain every figure shown.

## Sample data

All sample figures (recipes, prices, overheads, daily sales for Sept-Oct 2026) are **illustrative**, not real canteen
data. The textbook problems use the exact figures from the slides.
