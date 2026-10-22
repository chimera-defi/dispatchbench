from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    result = []

    def add(d):
        if d is not None and d >= start_date:
            result.append(d)

    if kind == "DAILY":
        step = int(parts[1])
        current = start_date
        while len(result) < count:
            result.append(current)
            current += timedelta(days=step)

    elif kind == "WEEKLY":
        step = int(parts[1])
        weekdays = sorted(("MO", "TU", "WE", "TH", "FR", "SA", "SU").index(
            code
        ) for code in parts[2].split(","))
        week_start = start_date - timedelta(days=start_date.weekday())
        week = 0
        while len(result) < count:
            monday = week_start + timedelta(weeks=week)
            for weekday in weekdays:
                add(monday + timedelta(days=weekday))
                if len(result) == count:
                    break
            week += step

    elif kind == "MONTHLY":
        step = int(parts[1])
        index = 0
        if len(parts) == 3:
            day_spec = int(parts[2])
            while len(result) < count:
                year = start_date.year + (start_date.month - 1 + index) // 12
                month = (start_date.month - 1 + index) % 12 + 1
                last_day = calendar.monthrange(year, month)[1]
                day = last_day if day_spec == -1 else day_spec
                if day <= last_day:
                    add(date(year, month, day))
                index += step
        else:
            n = int(parts[2])
            weekday = ("MO", "TU", "WE", "TH", "FR", "SA", "SU").index(parts[3])
            while len(result) < count:
                year = start_date.year + (start_date.month - 1 + index) // 12
                month = (start_date.month - 1 + index) % 12 + 1
                last_day = calendar.monthrange(year, month)[1]
                if n == -1:
                    last = date(year, month, last_day)
                    day = last_day - (last.weekday() - weekday) % 7
                else:
                    first_weekday = date(year, month, 1).weekday()
                    day = 1 + (weekday - first_weekday) % 7 + 7 * (n - 1)
                if day <= last_day:
                    add(date(year, month, day))
                index += step

    else:  # YEARLY
        step = int(parts[1])
        month, day = map(int, parts[2].split("-"))
        index = 0
        while len(result) < count:
            year = start_date.year + index
            try:
                add(date(year, month, day))
            except ValueError:
                pass
            index += step

    return [d.isoformat() for d in result]
