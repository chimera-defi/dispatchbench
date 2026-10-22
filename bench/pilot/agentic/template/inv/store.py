from .models import Item


class Store:
    def __init__(self):
        self.items: dict[str, Item] = {}

    def add_item(self, name: str, price_cents: int, qty: int = 1) -> None:
        if name in self.items:
            self.items[name].qty += qty
        else:
            self.items[name] = Item(name, price_cents, qty)

    def remove_item(self, name: str) -> None:
        del self.items[name]

    def total_cents(self) -> int:
        return sum(i.line_total() for i in self.items.values())
