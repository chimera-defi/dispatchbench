import calendar
from datetime import date, timedelta

WEEKDAYS = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    tokens = rule.split(" ")
    kind = tokens[0]
    out: list[date] = []

    if kind == "DAILY":
        k = int(tokens[1])
        d = start_date
        while len(out) < count:
            out.append(d)
            d += timedelta(days=k)

    elif kind == "WEEKLY":
        k = int(tokens[1])
        days = sorted(WEEKDAYS[c] for c in tokens[2].split(","))
        monday = start_date - timedelta(days=start_date.weekday())
        w = 0
        while len(out) < count:
            base = monday + timedelta(weeks=w * k)
            for wd in days:
                d = base + timedelta(days=wd)
                if d >= start_date and len(out) < count:
                    out.append(d)
            w += 1

    elif kind == "MONTHLY":
        k = int(tokens[1])
        base_index = start_date.year * 12 + start_date.month - 1
        i = 0
        while len(out) < count:
            y, m0 = divmod(base_index + i * k, 12)
            last = calendar.monthrange(y, m0 + 1)[1]
            d = None
            if len(tokens) == 3:
                dd = int(tokens[2])
                if dd == -1:
                    d = date(y, m0 + 1, last)
                elif dd <= last:
                    d = date(y, m0 + 1, dd)
            else:
                n = int(tokens[2])
                wd = WEEKDAYS[tokens[3]]
                if n == -1:
                    last_day = date(y, m0 + 1, last)
                    d = last_day - timedelta(days=(last_day.weekday() - wd) % 7)
                else:
                    first = date(y, m0 + 1, 1)
                    day = 1 + (wd - first.weekday()) % 7 + 7 * (n - 1)
                    if day <= last:
                        d = date(y, m0 + 1, day)
            if d is not None and d >= start_date:
                out.append(d)
            i += 1

    elif kind == "YEARLY":
        k = int(tokens[1])
        mm, dd = (int(x) for x in tokens[2].split("-"))
        i = 0
        while len(out) < count:
            y = start_date.year + i * k
            try:
                d = date(y, mm, dd)
            except ValueError:
                d = None
            if d is not None and d >= start_date:
                out.append(d)
            i += 1

    return [d.isoformat() for d in out[:count]]
