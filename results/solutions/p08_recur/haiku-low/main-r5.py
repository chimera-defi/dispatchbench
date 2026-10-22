import calendar
from datetime import date, timedelta
from typing import Iterator

_WD = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}


def _candidates(s: date, parts: list[str]) -> Iterator[date]:
    kind = parts[0]

    if kind == "DAILY":
        k = int(parts[1])
        i = 0
        while True:
            yield s + timedelta(days=i * k)
            i += 1

    elif kind == "WEEKLY":
        k = int(parts[1])
        days = sorted({_WD[c] for c in parts[2].split(",")})
        monday = s - timedelta(days=s.weekday())
        w = 0
        while True:
            for wd in days:
                yield monday + timedelta(weeks=w * k, days=wd)
            w += 1

    elif kind == "MONTHLY" and len(parts) == 3:
        k = int(parts[1])
        d_spec = int(parts[2])
        base = s.year * 12 + (s.month - 1)
        m = 0
        while True:
            y, mo = divmod(base + m * k, 12)
            mo += 1
            dim = calendar.monthrange(y, mo)[1]
            if d_spec == -1:
                yield date(y, mo, dim)
            elif d_spec <= dim:
                yield date(y, mo, d_spec)
            m += 1

    elif kind == "MONTHLY":
        k = int(parts[1])
        n = int(parts[2])
        wd = _WD[parts[3]]
        base = s.year * 12 + (s.month - 1)
        m = 0
        while True:
            y, mo = divmod(base + m * k, 12)
            mo += 1
            dim = calendar.monthrange(y, mo)[1]
            if n == -1:
                last = date(y, mo, dim)
                yield last - timedelta(days=(last.weekday() - wd) % 7)
            else:
                first = date(y, mo, 1)
                day = 1 + (wd - first.weekday()) % 7 + 7 * (n - 1)
                if day <= dim:
                    yield date(y, mo, day)
            m += 1

    elif kind == "YEARLY":
        k = int(parts[1])
        mm, dd = (int(x) for x in parts[2].split("-"))
        j = 0
        while True:
            try:
                yield date(s.year + j * k, mm, dd)
            except ValueError:
                pass
            j += 1

    else:
        raise ValueError(f"unknown rule: {rule_text_for_error(parts)}")


def rule_text_for_error(parts: list[str]) -> str:
    return " ".join(parts)


def recur(start: str, rule: str, count: int) -> list[str]:
    s = date.fromisoformat(start)
    out: list[str] = []
    for d in _candidates(s, rule.split()):
        if d >= s:
            out.append(d.isoformat())
            if len(out) >= count:
                break
    return out
