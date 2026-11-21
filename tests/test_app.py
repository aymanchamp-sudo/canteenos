"""Smoke test: every page renders without an exception (Streamlit AppTest).

Navigation changed from a radio widget to buttons + session_state['page'].
AppTest can inject session_state directly, so we pre-set the page key.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from streamlit.testing.v1 import AppTest

PAGES = [
    "Dashboard",
    "Recipe & BOM → Cost Sheet",
    "Batch Costing & EBQ",
    "Break-Even Analysis",
    "Daily Sales",
    "Monthly Trading & P&L",
    "Textbook Verification",
]


def test_all_pages_render():
    root = os.path.dirname(os.path.dirname(__file__))
    for p in PAGES:
        at = AppTest.from_file(os.path.join(root, "app.py"), default_timeout=60)
        at.session_state["page"] = p
        at.run()
        assert not at.exception, (p, [e.value for e in at.exception])
