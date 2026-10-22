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

    elif kind == "WEEKLY":
        k = int(tokens[1])
        days = {
            "MO": 0, "TU": 1, "WE": 2, "TH": 3,
            "FR": 4, "SA": 5, "SU": 6,
        }
        wanted = sorted(days[c] for c in tokens[2].split(","))
        monday = s - timedelta(days=s.weekday())
        week = 0
        done = False
        while not done:
            base = monday + timedelta(weeks=week * k)
            for wd in wanted:
                d = base + timedelta(days=wd)
                if d >= s and emit(d):
                    done = True
                    break
            week += 1

    elif kind == "MONTHLY":
        k = int(tokens[1])
        if len(tokens) == 3:
            dd = int(tokens[2])
            m_index = 0
            while len(out) < count:
                y = s.year + (s.month - 1 + m_index * k) // 12
                m = (s.month - 1 + m_index * k) % 12 + 1
                m_index += 1
                ndays = calendar.monthrange(y, m)[1]
                if dd == -1:
                    day = ndays
                elif 1 <= dd <= ndays:
                    day = dd
                else:
                    continue
                if emit(date(y, m, day)):
                    break
        else:
            n = int(tokens[2])
            wd = {
                "MO": 0, "TU": 1, "WE": 2, "TH": 3,
                "FR": 4, "SA": 5, "SU": 6,
            }[tokens[3]]
            m_index = 0
            while len(out) < count:
                y = s.year + (s.month - 1 + m_index * k) // 12
                m = (s.month - 1 + m_index * k) % 12 + 1
                m_index += 1
                ndays = calendar.monthrange(y, m)[1]
                if n == -1:
                    day = ndays
                    while date(y, m, day).weekday() != wd:
                        day -= 1
                else:
                    first = date(y, m, 1)
                    offset = (wd - first.weekday()) % 7
                    day = 1 + offset + 7 * (n - 1)
                    if day > ndays:
                        continue
                if emit(date(y, m, day)):
                    break

    elif kind == "YEARLY":
        k = int(tokens[1])
        mm, dd = (int(x) for x in tokens[2].split("-"))
        y = s.year
        while True:
            if (y - s.year) % k == 0:
                try:
                    d = date(y, mm, dd)
                except ValueError:
                    d = None
                if d is not None and emit(d):
                    break
            y += 1

    return out
