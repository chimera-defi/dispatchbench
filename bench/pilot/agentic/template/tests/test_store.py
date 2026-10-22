from inv.cli import main
from inv.money import format_cents
from inv.store import Store


def test_total():
    s = Store(); s.add_item("pen", 150, 2); s.add_item("pad", 399)
    assert s.total_cents() == 699
    assert main(["total"], s) == "$6.99"


def test_format():
    assert format_cents(5) == "$0.05" and format_cents(-1234) == "-$12.34"
