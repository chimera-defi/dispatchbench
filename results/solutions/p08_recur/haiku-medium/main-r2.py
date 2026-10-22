import calendar
from datetime import date, timedelta
from itertools import islice

_WD = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}


def _daily(s, k):
    d = s
    step = timedelta(days=k)
    while True:
        yield d
        d += step


def _weekly(s, k, days):
    monday = s - timedelta(days=s.weekday())
    wds = sorted(_WD[x] for x in days.split(","))
    w = 0
    while True:
        base = monday + timedelta(weeks=w)
        for wd in wds:
            d = base + timedelta(days=wd)
            if d >= s:
                yield d
        w += k


def _months(s, k):
    m = s.year * 12 + s.month - 1
    while True:
        y, mi = divmod(m, 12)
        yield y, mi + 1
        m += k


def _monthly_day(s, k, spec):
    for y, mo in _months(s, k):
        ndays = calendar.monthrange(y, mo)[1]
        if spec == -1:
            day = ndays
        elif spec <= ndays:
            day = spec
        else:
            continue
        d = date(y, mo, day)
        if d >= s:
            yield d


def _monthly_nth(s, k, n, wd):
    for y, mo in _months(s, k):
        ndays = calendar.monthrange(y, mo)[1]
        if n > 0:
            first = date(y, mo, 1)
            day = 1 + (wd - first.weekday()) % 7 + 7 * (n - 1)
            if day > ndays:
                continue
        else:
            last = date(y, mo, ndays)
            day = ndays - (last.weekday() - wd) % 7 + 7 * (n + 1)
        d = date(y, mo, day)
        if d >= s:
            yield d


def _yearly(s, k, mm, dd):
    j = 0
    while True:
        y = s.year + j * k
        j += 1
        try:
            d = date(y, mm, dd)
        except ValueError:
            continue
        if d >= s:
            yield d


def recur(start: str, rule: str, count: int) -> list[str]:
    s = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]

    if kind == "DAILY":
        gen = _daily(s, int(parts[1]))
    elif kind == "WEEKLY":
        gen = _weekly(s, int(parts[1]), parts[2])
    elif kind == "MONTHLY":
        k = int(parts[1])
        if len(parts) == 3:
            gen = _monthly_day(s, k, int(parts[2]))
        else:
            gen = _monthly_nth(s, k, int(parts[2]), _WD[parts[3]])
    elif kind == "YEARLY":
        mm, dd = (int(x) for x in parts[2].split("-"))
        gen = _yearly(s, int(parts[1]), mm, dd)
    else:
        raise ValueError(f"Unknown rule: {rule}")

    return [d.isoformat() for d in islice(gen, count)]
