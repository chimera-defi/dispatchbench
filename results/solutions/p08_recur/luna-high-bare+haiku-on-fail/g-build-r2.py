from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    result = []

    if kind == "DAILY":
        step = int(parts[1])
        current = start_date
        for _ in range(count):
            result.append(current.isoformat())
            current += timedelta(days=step)
        return result

    weekdays = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}

    if kind == "WEEKLY":
        interval = int(parts[1])
        days = sorted(weekdays[code] for code in parts[2].split(","))
        week_start = start_date - timedelta(days=start_date.weekday())
        week_index = 0

        while len(result) < count:
            monday = week_start + timedelta(weeks=week_index)
            for day in days:
                candidate = monday + timedelta(days=day)
                if candidate >= start_date:
                    result.append(candidate.isoformat())
                    if len(result) == count:
                        break
            week_index += interval
        return result

    if kind == "MONTHLY":
        interval = int(parts[1])
        month_index = 0

        while len(result) < count:
            year = start_date.year + (start_date.month - 1 + month_index) // 12
            month = (start_date.month - 1 + month_index) % 12 + 1
            last_day = calendar.monthrange(year, month)[1]

            if len(parts) == 3:
                day = int(parts[2])
                if day == -1:
                    day = last_day
                candidate = date(year, month, day) if day <= last_day else None
            else:
                ordinal = int(parts[2])
                target_weekday = weekdays[parts[3]]
                if ordinal == -1:
                    candidate = date(year, month, last_day)
                    candidate -= timedelta(days=(candidate.weekday() - target_weekday) % 7)
                else:
                    first = date(year, month, 1)
                    day = 1 + (target_weekday - first.weekday()) % 7 + 7 * (ordinal - 1)
                    candidate = date(year, month, day) if day <= last_day else None

            if candidate is not None and candidate >= start_date:
                result.append(candidate.isoformat())
            month_index += interval
        return result

    interval = int(parts[1])
    month, day = map(int, parts[2].split("-"))
    year_index = 0

    while len(result) < count:
        year = start_date.year + year_index
        try:
            candidate = date(year, month, day)
        except ValueError:
            candidate = None

        if candidate is not None and candidate >= start_date:
            result.append(candidate.isoformat())
        year_index += interval

    return result
