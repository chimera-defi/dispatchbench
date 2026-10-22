import calendar
from datetime import date, timedelta

_WD = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}


def _add_months(y, m, k):
    t = y * 12 + (m - 1) + k
    return t // 12, t % 12 + 1


def _month_days(y, m, d):
    last = calendar.monthrange(y, m)[1]
    if d == -1:
        return [date(y, m, last)]
    if d <= last:
        return [date(y, m, d)]
    return []


def _nth_weekday(y, m, n, wd):
    last = calendar.monthrange(y, m)[1]
    if n == -1:
        d = date(y, m, last)
        while d.weekday() != wd:
            d -= timedelta(days=1)
        return [d]
    first = date(y, m, 1)
    offset = (wd - first.weekday()) % 7
    day = 1 + offset + 7 * (n - 1)
    if day <= last:
        return [date(y, m, day)]
    return []


def recur(start: str, rule: str, count: int) -> list[str]:
    s = date.fromisoformat(start)
    parts = rule.split(" ")
    kind = parts[0]
    out = []

    if kind == "DAILY":
        k = int(parts[1])
        d = s
        while len(out) < count:
            out.append(d)
            d += timedelta(days=k)
        return [x.isoformat() for x in out]

    if kind == "WEEKLY":
        k = int(parts[1])
        days = sorted({_WD[c] for c in parts[2].split(",")})
        monday = s - timedelta(days=s.weekday())
        w = 0
        while len(out) < count:
            base = monday + timedelta(weeks=w * k)
            for wd in days:
                d = base + timedelta(days=wd)
                if d >= s:
                    out.append(d)
                    if len(out) == count:
                        break
            w += 1
        return [x.isoformat() for x in out]

    if kind == "MONTHLY":
        k = int(parts[1])
        if len(parts) == 3:
            dd = int(parts[2])
            gen = lambda y, m: _month_days(y, m, dd)
        else:
            n = int(parts[2])
            wd = _WD[parts[3]]
            gen = lambda y, m: _nth_weekday(y, m, n, wd)
        i = 0
        while len(out) < count:
            y, m = _add_months(s.year, s.month, i * k)
            for d in gen(y, m):
                if d >= s:
                    out.append(d)
                    if len(out) == count:
                        break
            i += 1
        return [x.isoformat() for x in out]

    if kind == "YEARLY":
        k = int(parts[1])
        mm, dd = map(int, parts[2].split("-"))
        i = 0
        while len(out) < count:
            y = s.year + i * k
            i += 1
            try:
                d = date(y, mm, dd)
            except ValueError:
                continue
            if d >= s:
                out.append(d)
        return [x.isoformat() for x in out]

    raise ValueError(f"unknown rule: {rule}")
