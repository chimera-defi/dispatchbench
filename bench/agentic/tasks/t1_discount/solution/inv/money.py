def format_cents(cents: int) -> str:
    """1234 -> '$12.34'; negative values get a leading '-'."""
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}${cents // 100}.{cents % 100:02d}"


def apply_percent(cents: int, pct: int) -> int:
    if not isinstance(pct, int) or isinstance(pct, bool) or not 0 <= pct <= 100:
        raise ValueError(pct)
    return (cents * (100 - pct) * 2 + 100) // 200
