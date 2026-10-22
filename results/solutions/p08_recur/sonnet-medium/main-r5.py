import datetime as dt
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    s = dt.date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    k = int(parts[1])
    res = []

    if kind == "DAILY":
        d = s
        while len(res) < count:
            res.append(d.isoformat())
            d += dt.timedelta(days=k)
        return res

    if kind == "WEEKLY":
        codes = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
        days = sorted(codes.index(c) for c in parts[2].split(","))
        monday = s - dt.timedelta(days=s.weekday())
        w = 0
        while len(res) < count:
            base = monday + dt.timedelta(weeks=w)
            for wd in days:
                d = base + dt.timedelta(days=wd)
                if d >= s:
                    res.append(d.isoformat())
                    if len(res) == count:
                        break
            w += k
        return res

    if kind == "MONTHLY":
        codes = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
        y, m = s.year, s.month
        while len(res) < count:
            dim = calendar.monthrange(y, m)[1]
            d = None
            if len(parts) == 3:
                D = int(parts[2])
                if D == -1:
                    d = dt.date(y, m, dim)
                elif D <= dim:
                    d = dt.date(y, m, D)
            else:
                N = int(parts[2])
                wd = codes.index(parts[3])
                cands = [dt.date(y, m, x) for x in range(1, dim + 1)
                         if dt.date(y, m, x).weekday() == wd]
                if N == -1:
                    d = cands[-1]
                elif N <= len(cands):
                    d = cands[N - 1]
            if d is not None and d >= s:
                res.append(d.isoformat())
            idx = y * 12 + (m - 1) + k
            y, m = idx // 12, idx % 12 + 1
        return res

    if kind == "YEARLY":
        mm, dd = map(int, parts[2].split("-"))
        y = s.year
        while len(res) < count:
            try:
                d = dt.date(y, mm, dd)
                if d >= s:
                    res.append(d.isoformat())
            except ValueError:
                pass
            y += k
        return res

    return res
