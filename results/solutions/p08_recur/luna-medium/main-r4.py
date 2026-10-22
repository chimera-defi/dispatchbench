from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    interval = int(parts[1])
    results = []

    def add_if_valid(candidate):
        if candidate is not None and candidate >= start_date:
            results.append(candidate)

    if kind == "DAILY":
        current = start_date
        step = timedelta(days=interval)
        for _ in range(count):
            results.append(current)
            current += step

    elif kind == "WEEKLY":
        weekdays = {
            "MO": 0, "TU": 1, "WE": 2, "TH": 3,
            "FR": 4, "SA": 5, "SU": 6,
        }
        selected = sorted(weekdays[day] for day in parts[2].split(","))
        start_monday = start_date - timedelta(days=start_date.weekday())
        week_index = 0
        while len(results) < count:
            monday = start_monday + timedelta(weeks=week_index)
            for weekday in selected:
                candidate = monday + timedelta(days=weekday)
                add_if_valid(candidate)
                if len(results) == count:
                    break
            week_index += interval

    elif kind == "MONTHLY":
        start_month_index = start_date.year * 12 + start_date.month - 1

        def month_date(year, month):
            if len(parts) == 3:
                day = int(parts[2])
                if day == -1:
                    day = calendar.monthrange(year, month)[1]
                elif day > calendar.monthrange(year, month)[1]:
                    return None
                return date(year, month, day)

            occurrence = int(parts[2])
            weekday_code = parts[3]
            weekday = {
                "MO": 0, "TU": 1, "WE": 2, "TH": 3,
                "FR": 4, "SA": 5, "SU": 6,
            }[weekday_code]
            days_in_month = calendar.monthrange(year, month)[1]
            matching = [
                day for day in range(1, days_in_month + 1)
                if date(year, month, day).weekday() == weekday
            ]
            index = occurrence - 1 if occurrence > 0 else -1
            if occurrence > 0 and occurrence > len(matching):
                return None
            return date(year, month, matching[index])

        month_index = 0
        while len(results) < count:
            absolute_month = start_month_index + month_index * interval
            year, month_zero_based = divmod(absolute_month, 12)
            month = month_zero_based + 1
            candidate = month_date(year, month)
            add_if_valid(candidate)
            month_index += 1

    elif kind == "YEARLY":
        month, day = map(int, parts[2].split("-"))
        year_index = 0
        while len(results) < count:
            year = start_date.year + year_index * interval
            try:
                candidate = date(year, month, day)
            except ValueError:
                candidate = None
            add_if_valid(candidate)
            year_index += 1

    return [candidate.isoformat() for candidate in results]
