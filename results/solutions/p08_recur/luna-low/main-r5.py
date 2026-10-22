from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    step = int(parts[1])
    results = []

    def add_if_valid(y, m, d):
        if d is not None:
            candidate = date(y, m, d)
            if candidate >= start_date:
                results.append(candidate)

    if kind == "DAILY":
        current = start_date
        delta = timedelta(days=step)
        for _ in range(count):
            results.append(current)
            current += delta

    elif kind == "WEEKLY":
        weekdays = {code: i for i, code in enumerate(
            ("MO", "TU", "WE", "TH", "FR", "SA", "SU")
        )}
        selected = sorted(weekdays[code] for code in parts[2].split(","))
        start_week = start_date - timedelta(days=start_date.weekday())
        week = 0
        while len(results) < count:
            week_start = start_week + timedelta(weeks=week)
            for weekday in selected:
                candidate = week_start + timedelta(days=weekday)
                if candidate >= start_date:
                    results.append(candidate)
                    if len(results) == count:
                        break
            week += step

    elif kind == "MONTHLY":
        index = 0
        if len(parts) == 3:
            day_rule = int(parts[2])
            while len(results) < count:
                year, month = divmod(start_date.year * 12 + start_date.month - 1 + index, 12)
                month += 1
                last_day = calendar.monthrange(year, month)[1]
                day = last_day if day_rule == -1 else (
                    day_rule if day_rule <= last_day else None
                )
                add_if_valid(year, month, day)
                index += step
        else:
            nth = int(parts[2])
            weekday = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                       "FR": 4, "SA": 5, "SU": 6}[parts[3]]
            while len(results) < count:
                year, month = divmod(start_date.year * 12 + start_date.month - 1 + index, 12)
                month += 1
                last_day = calendar.monthrange(year, month)[1]
                if nth == -1:
                    day = last_day - ((date(year, month, last_day).weekday() - weekday) % 7)
                else:
                    day = 1 + ((weekday - date(year, month, 1).weekday()) % 7) + 7 * (nth - 1)
                    if day > last_day:
                        day = None
                add_if_valid(year, month, day)
                index += step

    elif kind == "YEARLY":
        month, day_rule = map(int, parts[2].split("-"))
        year = start_date.year
        while len(results) < count:
            try:
                candidate = date(year, month, day_rule)
            except ValueError:
                candidate = None
            if candidate is not None and candidate >= start_date:
                results.append(candidate)
            year += step

    return [d.isoformat() for d in results]
