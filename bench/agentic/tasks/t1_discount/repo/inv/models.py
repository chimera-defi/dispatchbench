from dataclasses import dataclass


@dataclass
class Item:
    name: str
    price_cents: int
    qty: int = 1

    def line_total(self) -> int:
        return self.price_cents * self.qty
