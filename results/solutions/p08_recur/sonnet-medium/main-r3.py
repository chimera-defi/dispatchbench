from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    y, m, d = map(int, start.split("-"))
    s = date(y, m, d)
    parts = rule.split()
    kind = parts[0]
    K = int(parts[1])
    res = []

    if kind == "DAILY":
        cur = s
        while len(res) < count:
            res.append(cur.isoformat())
            cur += timedelta(days=K * 1)
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
            w += K
        return res

    if kind == "MONTHLY":
        idx = 0
        while len(res) < count:
            total = s.year * 12 + (s.month - 1) + idx
            yy, mm = divmod(total, 12)
            mm += 1
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
                first = date(yy, mm, 1)
                off = (wd - first.weekday()) % 7
                dates = [1 + off + 7 * i for i in range(5) if 1 + off + 7 * i <= dim]
                if N == -1:
                    cur = date(yy, mm, dates[-1])
                elif N <= len(dates):
                    cur = date(yy, mm, dates[N - 1])
            if cur is not None and cur >= s:
                res.append(cur.isoformat())
            idx += K
        return res

    if kind == "YEARLY":
        mm, dd = map(int, parts[2].split("-"))
        yy = s.year
        while len(res) < count:
            try:
                cur = date(yy, mm, dd)
                if cur >= s:
                    res.append(cur.isoformat())
            except ValueError:
                pass
            yy += K
        return res

    return res
