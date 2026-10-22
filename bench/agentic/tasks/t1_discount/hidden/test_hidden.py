import pytest
from inv.cli import main
from inv.money import apply_percent, format_cents
from inv.store import Store

def test_round_half_up():
    assert apply_percent(1005, 10) == 905      # 904.5 -> 905 (banker's would give 904)
    assert apply_percent(25, 50) == 13         # 12.5 -> 13
    assert apply_percent(999, 0) == 999 and apply_percent(999, 100) == 0
    assert apply_percent(333, 33) == 223       # 223.11
@pytest.mark.parametrize("bad", [-1, 101, 10.5, "10"])
def test_pct_bounds(bad):
    with pytest.raises(ValueError): apply_percent(100, bad)
def test_codes():
    s = Store(); s.add_item("a", 1005); s.add_code("Save10", 10)
    assert s.total_cents() == 1005 and s.total_cents("SAVE10") == 905 and s.total_cents("save10") == 905
    with pytest.raises(ValueError): s.add_code("SAVE10", 20)
    with pytest.raises(ValueError): s.add_code("X", 150)
    with pytest.raises(KeyError): s.total_cents("nope")
def test_cli():
    s = Store(); s.add_item("a", 1005); s.add_code("half", 50)
    assert main(["total"], s) == "$10.05"
    assert main(["total", "--code", "HALF"], s) == "$5.03"
    assert main(["total", "--code", "Nope"], s) == "unknown code: Nope"
    assert main(["list"], s) == "a x1 $10.05"
