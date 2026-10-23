from datetime import date, timedelta
from calendar import monthrange


def recur(start: str, rule: str, count: int) -> list[str]:
    first = date.fromisoformat(start)
    parts = rule.split()
    kind, step = parts[0], int(parts[1])
    weekdays = {name: i for i, name in enumerate(
        ("MO", "TU", "WE", "TH", "FR", "SA", "SU")
    )}
    result = []

    if kind == "DAILY":
        return [
            (first + timedelta(days=i * step)).isoformat()
            for i in range(count)
        ]

    if kind == "WEEKLY":
        days = sorted(weekdays[name] for name in parts[2].split(","))
        monday = first - timedelta(days=first.weekday())
        while len(result) < count:
            for day in days:
                candidate = monday + timedelta(days=day)
                if candidate >= first:
                    result.append(candidate.isoformat())
                    if len(result) == count:
                        return result
            monday += timedelta(weeks=step)

    elif kind == "MONTHLY":
        month_index = first.year * 12 + first.month - 1
        while len(result) < count:
            year, month_zero = divmod(month_index, 12)
            month = month_zero + 1
            first_weekday, last_day = monthrange(year, month)

            if len(parts) == 3:
                requested = int(parts[2])
                day = last_day if requested == -1 else requested
            else:
                n = int(parts[2])
                weekday = weekdays[parts[3]]
                if n == -1:
                    last_weekday = (first_weekday + last_day - 1) % 7
                    day = last_day - (last_weekday - weekday) % 7
                else:
                    day = 1 + (weekday - first_weekday) % 7 + 7 * (n - 1)

            if day <= last_day:
                candidate = date(year, month, day)
                if candidate >= first:
                    result.append(candidate.isoformat())
            month_index += step

    elif kind == "YEARLY":
        month, day = map(int, parts[2].split("-"))
        year = first.year
        while len(result) < count:
            if day <= monthrange(year, month)[1]:
                candidate = date(year, month, day)
                if candidate >= first:
                    result.append(candidate.isoformat())
            year += step

    return result
