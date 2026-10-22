import datetime as dt
from itertools import islice

_DAYS = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
_END = dt.date(3000, 1, 1)


def _days_in_month(y, m):
    nxt = dt.date(y + (m == 12), m % 12 + 1, 1)
    return (nxt - dt.timedelta(days=1)).day


def _daily(s, k):
    d = s
    while d < _END:
        yield d
        d += dt.timedelta(days=k)


def _weekly(s, k, codes):
    wds = sorted(_DAYS.index(c) for c in codes.split(","))
    mon = s - dt.timedelta(days=s.weekday())
    w = 0
    while True:
        for wd in wds:
            d = mon + dt.timedelta(days=7 * w + wd)
            if d >= _END:
                return
            if d >= s:
                yield d
        w += k


def _month_candidate(y, m, spec):
    last = _days_in_month(y, m)
    if spec[0] == "day":
        day = spec[1]
        if day == -1:
            day = last
        return dt.date(y, m, day) if day <= last else None
    _, n, wd = spec
    if n > 0:
        first = dt.date(y, m, 1).weekday()
        day = 1 + (wd - first) % 7 + 7 * (n - 1)
        return dt.date(y, m, day) if day <= last else None
    lastwd = dt.date(y, m, last).weekday()
    return dt.date(y, m, last - (lastwd - wd) % 7)


def _monthly(s, k, spec):
    base = s.year * 12 + s.month - 1
    j = 0
    while True:
        y, m = divmod(base + j * k, 12)
        m += 1
        j += 1
        if y >= 3000:
            return
        d = _month_candidate(y, m, spec)
        if d is not None and d >= s:
            yield d


def _yearly(s, k, md):
    mm, dd = map(int, md.split("-"))
    j = 0
    while True:
        y = s.year + j * k
        j += 1
        if y >= 3000:
            return
        try:
            d = dt.date(y, mm, dd)
        except ValueError:
            continue
        if d >= s:
            yield d


def recur(start: str, rule: str, count: int) -> list[str]:
    s = dt.date.fromisoformat(start)
    p = rule.split()
    if p[0] == "DAILY":
        gen = _daily(s, int(p[1]))
    elif p[0] == "WEEKLY":
        gen = _weekly(s, int(p[1]), p[2])
    elif p[0] == "MONTHLY":
        if len(p) == 3:
            spec = ("day", int(p[2]))
        else:
            spec = ("nth", int(p[2]), _DAYS.index(p[3]))
        gen = _monthly(s, int(p[1]), spec)
    else:
        gen = _yearly(s, int(p[1]), p[2])
    return [d.isoformat() for d in islice(gen, count)]
