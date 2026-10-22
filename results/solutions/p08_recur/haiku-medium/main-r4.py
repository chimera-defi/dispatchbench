import calendar
from datetime import date, timedelta
from itertools import islice

_WD = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}


def _daily(s, k):
    i = 0
    while True:
        yield s + timedelta(days=i * k)
        i += 1


def _weekly(s, k, days):
    monday = s - timedelta(days=s.weekday())
    wds = sorted(_WD[x] for x in days.split(","))
    w = 0
    while True:
        base = monday + timedelta(weeks=w * k)
        for wd in wds:
            d = base + timedelta(days=wd)
            if d >= s:
                yield d
        w += 1


def _month_iter(s, k):
    base_idx = s.year * 12 + (s.month - 1)
    j = 0
    while True:
        yy, mm0 = divmod(base_idx + j * k, 12)
        yield yy, mm0 + 1
        j += 1


def _monthly_day(s, k, dd):
    for yy, mm in _month_iter(s, k):
        ndays = calendar.monthrange(yy, mm)[1]
        day = ndays if dd == -1 else dd
        if day <= ndays:
            d = date(yy, mm, day)
            if d >= s:
                yield d


def _monthly_nth(s, k, n, wd):
    for yy, mm in _month_iter(s, k):
        ndays = calendar.monthrange(yy, mm)[1]
        if n > 0:
            first = date(yy, mm, 1)
            off = (wd - first.weekday()) % 7
            day = 1 + off + 7 * (n - 1)
            if day <= ndays:
                d = date(yy, mm, day)
                if d >= s:
                    yield d
        else:
            last = date(yy, mm, ndays)
            off = (last.weekday() - wd) % 7
            d = last - timedelta(days=off)
            if d >= s:
                yield d


def _yearly(s, k, mm, dd):
    j = 0
    while True:
        yy = s.year + j * k
        try:
            d = date(yy, mm, dd)
        except ValueError:
            d = None
        if d is not None and d >= s:
            yield d
        j += 1


def recur(start: str, rule: str, count: int) -> list[str]:
    s = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]

    if kind == "DAILY":
        gen = _daily(s, int(parts[1]))
    elif kind == "WEEKLY":
        gen = _weekly(s, int(parts[1]), parts[2])
    elif kind == "MONTHLY":
        if len(parts) == 3:
            gen = _monthly_day(s, int(parts[1]), int(parts[2]))
        else:
            gen = _monthly_nth(s, int(parts[1]), int(parts[2]), _WD[parts[3]])
    elif kind == "YEARLY":
        mm, dd = (int(x) for x in parts[2].split("-"))
        gen = _yearly(s, int(parts[1]), mm, dd)
    else:
        raise ValueError(f"unknown rule: {rule}")

    return [d.isoformat() for d in islice(gen, count)]
