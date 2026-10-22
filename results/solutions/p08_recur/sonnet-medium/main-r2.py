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
        return res

    if kind == "WEEKLY":
        codes = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
        days = sorted(codes.index(c) for c in parts[2].split(","))
        monday = s - timedelta(days=s.weekday())
        w = 0
        while len(res) < count:
            base = monday + timedelta(weeks=w)
            for wd in days:
                cur = base + timedelta(days=wd)
                if cur >= s:
                    res.append(cur.isoformat())
                    if len(res) == count:
                        break
            w += k
        return res

    if kind == "MONTHLY":
        idx = 0
        while len(res) < count:
            tot = s.year * 12 + (s.month - 1) + idx
            yy, mm = divmod(tot, 12)
            mm += 1
            idx += k
            if yy > 3000:
                break
            dim = calendar.monthrange(yy, mm)[1]
            cur = None
            if len(parts) == 3:
                D = int(parts[2])
                if D == -1:
                    cur = date(yy, mm, dim)
                elif D <= dim:
                    cur = date(yy, mm, D)
            else:
                N = int(parts[2])
                wd = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"].index(parts[3])
                if N == -1:
                    last = date(yy, mm, dim)
                    cur = last - timedelta(days=(last.weekday() - wd) % 7)
                else:
                    first = date(yy, mm, 1)
                    day = 1 + (wd - first.weekday()) % 7 + 7 * (N - 1)
                    if day <= dim:
                        cur = date(yy, mm, day)
            if cur is not None and cur >= s:
                res.append(cur.isoformat())
        return res

    if kind == "YEARLY":
        mm, dd = map(int, parts[2].split("-"))
        yy = s.year
        while len(res) < count and yy < 3000:
            try:
                cur = date(yy, mm, dd)
                if cur >= s:
                    res.append(cur.isoformat())
            except ValueError:
                pass
            yy += k
        return res

    return res
