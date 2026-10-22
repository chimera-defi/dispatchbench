from datetime import date, timedelta
import calendar


_WD = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}


def _month_add(y, m, n):
    t = y * 12 + (m - 1) + n
    return t // 12, t % 12 + 1


def _nth_weekday(y, m, wd, n):
    first = date(y, m, 1)
    if n > 0:
        offset = (wd - first.weekday()) % 7
        d = first + timedelta(days=offset + 7 * (n - 1))
        return d if d.month == m else None
    last_day = calendar.monthrange(y, m)[1]
    last = date(y, m, last_day)
    offset = (last.weekday() - wd) % 7
    d = last - timedelta(days=offset + 7 * (-n - 1))
    return d if d.month == m else None


def recur(start: str, rule: str, count: int) -> list[str]:
    s = date.fromisoformat(start)
    parts = rule.split(" ")
    kind = parts[0]
    result = []

    if kind == "DAILY":
        k = int(parts[1])
        d = s
        while len(result) < count:
            result.append(d.isoformat())
            d += timedelta(days=k)
        return result

    if kind == "WEEKLY":
        k = int(parts[1])
        days = sorted({_WD[c] for c in parts[2].split(",")})
        monday0 = s - timedelta(days=s.weekday())
        w = 0
        while len(result) < count:
            base = monday0 + timedelta(weeks=w * k)
            for wd in days:
                d = base + timedelta(days=wd)
                if d >= s:
                    result.append(d.isoformat())
                    if len(result) == count:
                        break
            w += 1
        return result

    if kind == "MONTHLY":
        k = int(parts[1])
        if len(parts) == 3:
            D = int(parts[2])
            i = 0
            while len(result) < count:
                y, m = _month_add(s.year, s.month, i * k)
                ndays = calendar.monthrange(y, m)[1]
                if D == -1:
                    day = ndays
                elif D <= ndays:
                    day = D
                else:
                    day = None
                if day is not None:
                    d = date(y, m, day)
                    if d >= s:
                        result.append(d.isoformat())
                i += 1
            return result
        n = int(parts[2])
        wd = _WD[parts[3]]
        i = 0
        while len(result) < count:
            y, m = _month_add(s.year, s.month, i * k)
            d = _nth_weekday(y, m, wd, n)
            if d is not None and d >= s:
                result.append(d.isoformat())
            i += 1
        return result

    if kind == "YEARLY":
        k = int(parts[1])
        mm, dd = (int(x) for x in parts[2].split("-"))
        i = 0
        while len(result) < count:
            y = s.year + i * k
            if mm == 2 and dd == 29 and not calendar.isleap(y):
                i += 1
                continue
            d = date(y, mm, dd)
            if d >= s:
                result.append(d.isoformat())
            i += 1
        return result

    raise ValueError(f"unknown rule: {rule}")
