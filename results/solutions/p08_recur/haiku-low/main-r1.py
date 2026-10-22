import datetime
import calendar


WEEKDAY_CODES = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]


def _add_months(year: int, month: int, delta: int) -> tuple[int, int]:
    total = year * 12 + (month - 1) + delta
    return total // 12, total % 12 + 1


def _nth_weekday_of_month(year: int, month: int, weekday: int, n: int):
    first_wd, days_in_month = calendar.monthrange(year, month)
    if n > 0:
        first = 1 + (weekday - first_wd) % 7
        day = first + 7 * (n - 1)
        return day if day <= days_in_month else None
    last = days_in_month - (first_wd + days_in_month - 1 - weekday) % 7
    day = last + 7 * (n + 1)
    return day if day >= 1 else None


def recur(start: str, rule: str, count: int) -> list[str]:
    s = datetime.date.fromisoformat(start)
    tokens = rule.split(" ")
    kind = tokens[0]
    result: list[str] = []

    if kind == "DAILY":
        k = int(tokens[1])
        cur = s
        while len(result) < count:
            result.append(cur.isoformat())
            cur += datetime.timedelta(days=k)
        return result

    if kind == "WEEKLY":
        k = int(tokens[1])
        days = {WEEKDAY_CODES.index(c) for c in tokens[2].split(",")}
        monday = s - datetime.timedelta(days=s.weekday())
        week = 0
        while len(result) < count:
            if week % k == 0:
                for wd in sorted(days):
                    d = monday + datetime.timedelta(weeks=week, days=wd)
                    if d >= s:
                        result.append(d.isoformat())
                        if len(result) == count:
                            return result
            week += 1
        return result

    if kind == "MONTHLY":
        k = int(tokens[1])
        year, month = s.year, s.month
        month_index = 0
        while len(result) < count:
            if month_index % k == 0:
                if len(tokens) == 3:
                    d_val = int(tokens[2])
                    _, dim = calendar.monthrange(year, month)
                    if d_val == -1:
                        day = dim
                    elif 1 <= d_val <= dim:
                        day = d_val
                    else:
                        day = None
                    candidates = [day] if day is not None else []
                else:
                    n = int(tokens[2])
                    wd = WEEKDAY_CODES.index(tokens[3])
                    day = _nth_weekday_of_month(year, month, wd, n)
                    candidates = [day] if day is not None else []
                for day in candidates:
                    d = datetime.date(year, month, day)
                    if d >= s:
                        result.append(d.isoformat())
                        if len(result) == count:
                            return result
            month_index += 1
            year, month = _add_months(year, month, 1)
        return result

    if kind == "YEARLY":
        k = int(tokens[1])
        mm, dd = (int(x) for x in tokens[2].split("-"))
        year = s.year
        year_index = 0
        while len(result) < count:
            if year_index % k == 0:
                try:
                    d = datetime.date(year, mm, dd)
                except ValueError:
                    d = None
                if d is not None and d >= s:
                    result.append(d.isoformat())
            year += 1
            year_index += 1
        return result

    raise ValueError(f"Unknown rule: {rule}")
