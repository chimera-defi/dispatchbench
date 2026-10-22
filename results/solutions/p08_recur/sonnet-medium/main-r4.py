from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    y, m, d = map(int, start.split("-"))
    s = date(y, m, d)
    parts = rule.split()
    kind = parts[0]
    k = int(parts[1])
    res = []

    if kind == "DAILY":
        cur = s
        while len(res) < count:
            res.append(cur.isoformat())
            cur += timedelta(days=k)

    elif kind == "WEEKLY":
        codes = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
        wds = sorted(codes.index(c) for c in parts[2].split(","))
        monday = s - timedelta(days=s.weekday())
        w = 0
        while len(res) < count:
            base = monday + timedelta(weeks=w)
            for wd in wds:
                dt = base + timedelta(days=wd)
                if dt >= s:
                    res.append(dt.isoformat())
                    if len(res) == count:
                        break
            w += k

    elif kind == "MONTHLY":
        idx = 0
        while len(res) < count:
            total = (s.year * 12 + s.month - 1) + idx
            yy, mm = divmod(total, 12)
            mm += 1
            idx += k
            dim = calendar.monthrange(yy, mm)[1]
            dt = None
            if len(parts) == 3:
                dd = int(parts[2])
                if dd == -1:
                    dd = dim
                if dd <= dim:
                    dt = date(yy, mm, dd)
            else:
                n = int(parts[2])
                wd = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"].index(parts[3])
                days = [x for x in range(1, dim + 1)
                        if date(yy, mm, x).weekday() == wd]
                if n == -1:
                    dt = date(yy, mm, days[-1])
                elif n <= len(days):
                    dt = date(yy, mm, days[n - 1])
            if dt is not None and dt >= s:
                res.append(dt.isoformat())

    else:  # YEARLY
        mm, dd = map(int, parts[2].split("-"))
        yy = s.year
        while len(res) < count:
            try:
                dt = date(yy, mm, dd)
                if dt >= s:
                    res.append(dt.isoformat())
            except ValueError:
                pass
            yy += k

    return res
