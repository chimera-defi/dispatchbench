from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    s = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    k = int(parts[1])
    res = []

    if kind == "DAILY":
        d = s
        while len(res) < count:
            res.append(d.isoformat())
            d += timedelta(days=k)
        return res

    if kind == "WEEKLY":
        codes = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
        wds = sorted(codes.index(c) for c in parts[2].split(","))
        monday = s - timedelta(days=s.weekday())
        w = 0
        while len(res) < count:
            base = monday + timedelta(weeks=w)
            for wd in wds:
                d = base + timedelta(days=wd)
                if d >= s:
                    res.append(d.isoformat())
                    if len(res) == count:
                        break
            w += k
        return res

    if kind == "MONTHLY":
        idx = s.year * 12 + s.month - 1
        m = 0
        nth_mode = len(parts) == 4
        while len(res) < count:
            y, mo = divmod(idx + m, 12)
            mo += 1
            dim = calendar.monthrange(y, mo)[1]
            d = None
            if not nth_mode:
                D = int(parts[2])
                if D == -1:
                    d = date(y, mo, dim)
                elif D <= dim:
                    d = date(y, mo, D)
            else:
                N = int(parts[2])
                wd = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"].index(parts[3])
                days = [x for x in range(1, dim + 1)
                        if date(y, mo, x).weekday() == wd]
                if N == -1:
                    d = date(y, mo, days[-1])
                elif N <= len(days):
                    d = date(y, mo, days[N - 1])
            if d is not None and d >= s:
                res.append(d.isoformat())
            m += k
        return res

    if kind == "YEARLY":
        mm, dd = map(int, parts[2].split("-"))
        y = s.year
        while len(res) < count:
            try:
                d = date(y, mm, dd)
            except ValueError:
                d = None
            if d is not None and d >= s:
                res.append(d.isoformat())
            y += k
        return res

    return res
