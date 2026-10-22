from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    s = date.fromisoformat(start)
    tokens = rule.split(" ")
    kind = tokens[0]
    out: list[str] = []

    def emit(d: date) -> bool:
        if d >= s:
            out.append(d.isoformat())
        return len(out) >= count

    if kind == "DAILY":
        k = int(tokens[1])
        d = s
        while True:
            if emit(d):
                break
            d += timedelta(days=k)
        return out

    if kind == "WEEKLY":
        k = int(tokens[1])
        codes = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}
        days = sorted({codes[c] for c in tokens[2].split(",")})
        monday = s - timedelta(days=s.weekday())
        week = 0
        while True:
            base = monday + timedelta(weeks=week * k)
            for wd in days:
                d = base + timedelta(days=wd)
                if d >= s and emit(d):
                    return out
            week += 1

    if kind == "MONTHLY":
        k = int(tokens[1])
        second = tokens[2]
        if len(tokens) == 3:
            # MONTHLY K D
            dom = int(second)
            y, m = s.year, s.month
            idx = 0
            while True:
                if idx % k == 0:
                    last = calendar.monthrange(y, m)[1]
                    if dom == -1:
                        day = last
                    else:
                        day = dom
                    if 1 <= day <= last:
                        d = date(y, m, day)
                        if d >= s and emit(d):
                            return out
                m += 1
                if m > 12:
                    m = 1
                    y += 1
                idx += 1
        else:
            # MONTHLY K N WD
            n = int(second)
            wd = codes_wd = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}[tokens[3]]
            y, m = s.year, s.month
            idx = 0
            while True:
                if idx % k == 0:
                    last = calendar.monthrange(y, m)[1]
                    if n > 0:
                        first = date(y, m, 1)
                        offset = (wd - first.weekday()) % 7
                        day = 1 + offset + 7 * (n - 1)
                        if day > last:
                            day = None
                    else:
                        lastd = date(y, m, last)
                        offset = (lastd.weekday() - wd) % 7
                        day = last - offset
                        # n == -1 is the last such weekday
                    if day is not None:
                        d = date(y, m, day)
                        if d >= s and emit(d):
                            return out
                m += 1
                if m > 12:
                    m = 1
                    y += 1
                idx += 1

    if kind == "YEARLY":
        k = int(tokens[1])
        mm, dd = (int(x) for x in tokens[2].split("-"))
        y = s.year
        idx = 0
        while True:
            if idx % k == 0:
                if not (mm == 2 and dd == 29 and not calendar.isleap(y)):
                    d = date(y, mm, dd)
                    if d >= s and emit(d):
                        return out
            y += 1
            idx += 1

    return out
