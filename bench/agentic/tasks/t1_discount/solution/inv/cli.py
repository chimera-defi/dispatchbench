from .money import format_cents
from .store import Store


def main(argv: list[str], store: Store) -> str:
    """Tiny command interface. Returns the output text."""
    if not argv:
        return "usage: total | list"
    cmd = argv[0]
    if cmd == "total":
        if argv[1:2] == ["--code"]:
            try: return format_cents(store.total_cents(argv[2]))
            except KeyError: return f"unknown code: {argv[2]}"
        return format_cents(store.total_cents())
    if cmd == "list":
        return "\n".join(f"{i.name} x{i.qty} {format_cents(i.line_total())}" for i in store.items.values())
    return f"unknown command: {cmd}"
