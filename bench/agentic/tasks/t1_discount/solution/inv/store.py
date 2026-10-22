from .models import Item
from .money import apply_percent


class Store:
    def __init__(self):
        self.items: dict[str, Item] = {}
        self.codes: dict[str, int] = {}

    def add_code(self, code, pct):
        k = code.lower()
        if k in self.codes: raise ValueError(code)
        apply_percent(0, pct)
        self.codes[k] = pct

    def add_item(self, name: str, price_cents: int, qty: int = 1) -> None:
        if name in self.items:
            self.items[name].qty += qty
        else:
            self.items[name] = Item(name, price_cents, qty)

    def remove_item(self, name: str) -> None:
        del self.items[name]

    def total_cents(self, code=None) -> int:
        t = sum(i.line_total() for i in self.items.values())
        return t if code is None else apply_percent(t, self.codes[code.lower()])
