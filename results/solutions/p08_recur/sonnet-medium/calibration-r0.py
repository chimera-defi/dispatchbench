import datetime as _dt
import calendar as _cal


def recur(start: str, rule: str, count: int) -> list[str]:
    s = _dt.date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    k = int(parts[1])
    res = []

    if kind == "DAILY":
        d = s
        step = _dt.timedelta(days=k)
        while len(res) < count:
            res.append(d.isoformat())
            d += step
        return res

    if kind == "WEEKLY":
        codes = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
        wds = sorted(codes.index(c) for c in parts[2].split(","))
        monday = s - _dt.timedelta(days=s.weekday())
        w = 0
        while len(res) < count:
            base = monday + _dt.timedelta(weeks=w)
            for wd in wds:
                d = base + _dt.timedelta(days=wd)
                if d >= s:
                    res.append(d.isoformat())
                    if len(res) == count:
                        break
            w += k
        return res

    if kind == "MONTHLY":
        y, m = s.year, s.month
        codes = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
        while len(res) < count:
            dim = _cal.monthrange(y, m)[1]
            d = None
            if len(parts) == 3:
                D = int(parts[2])
                if D == -1:
                    d = _dt.date(y, m, dim)
                elif D <= dim:
                    d = _dt.date(y, m, D)
            else:
                N = int(parts[2])
                wd = codes.index(parts[3])
                days = [x for x in range(1, dim + 1)
                        if _dt.date(y, m, x).weekday() == wd]
                if N == -1:
                    d = _dt.date(y, m, days[-1])
                elif N <= len(days):
                    d = _dt.date(y, m, days[N - 1])
            if d is not None and d >= s:
                res.append(d.isoformat())
            t = y * 12 + (m - 1) + k
            y, m = t // 12, t % 12 + 1
        return res

    if kind == "YEARLY":
        mm, dd = map(int, parts[2].split("-"))
        y = s.year
        while len(res) < count:
            try:
                d = _dt.date(y, mm, dd)
                if d >= s:
                    res.append(d.isoformat())
            except ValueError:
                pass
            y += k
        return res

    return res
