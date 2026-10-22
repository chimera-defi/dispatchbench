from datetime import date, timedelta
import calendar

NAMES = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]


def recur(start: str, rule: str, count: int) -> list[str]:
    s = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    res: list[date] = []

    if kind == "DAILY":
        k = int(parts[1])
        d = s
        while len(res) < count:
            res.append(d)
            d += timedelta(days=k)

    elif kind == "WEEKLY":
        k = int(parts[1])
        wds = sorted({NAMES.index(x) for x in parts[2].split(",")})
        monday0 = s - timedelta(days=s.weekday())
        week = 0
        while len(res) < count:
            if week % k == 0:
                mon = monday0 + timedelta(weeks=week)
                for wd in wds:
                    d = mon + timedelta(days=wd)
                    if d >= s:
                        res.append(d)
            week += 1

    elif kind == "MONTHLY" and len(parts) == 3:
        k = int(parts[1])
        D = int(parts[2])
        base = s.year * 12 + (s.month - 1)
        idx = base
        while len(res) < count:
            if (idx - base) % k == 0:
                y, m = idx // 12, idx % 12 + 1
                ndays = calendar.monthrange(y, m)[1]
                day = ndays if D == -1 else D
                if 1 <= day <= ndays:
                    d = date(y, m, day)
                    if d >= s:
                        res.append(d)
            idx += 1

    elif kind == "MONTHLY":
        k = int(parts[1])
        n = int(parts[2])
        wd = NAMES.index(parts[3])
        base = s.year * 12 + (s.month - 1)
        idx = base
        while len(res) < count:
            if (idx - base) % k == 0:
                y, m = idx // 12, idx % 12 + 1
                ndays = calendar.monthrange(y, m)[1]
                if n == -1:
                    last = date(y, m, ndays)
                    d = last - timedelta(days=(last.weekday() - wd) % 7)
                else:
                    first = date(y, m, 1)
                    d = first + timedelta(days=(wd - first.weekday()) % 7 + 7 * (n - 1))
                    if d.month != m:
                        d = None
                if d is not None and d >= s:
                    res.append(d)
            idx += 1

    elif kind == "YEARLY":
        k = int(parts[1])
        mm, dd = (int(x) for x in parts[2].split("-"))
        j = 0
        while len(res) < count:
            try:
                d = date(s.year + j, mm, dd)
            except ValueError:
                d = None
            if d is not None and d >= s:
                res.append(d)
            j += k

    return [d.isoformat() for d in res[:count]]
