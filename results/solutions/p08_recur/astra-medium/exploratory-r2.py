from datetime import date, timedelta
from calendar import monthrange


def recur(start: str, rule: str, count: int) -> list[str]:
    first = date.fromisoformat(start)
    parts = rule.split()
    kind, step = parts[0], int(parts[1])
    weekdays = {code: i for i, code in enumerate(
        ("MO", "TU", "WE", "TH", "FR", "SA", "SU")
    )}
    result = []

    def add(candidate):
        if candidate >= first:
            result.append(candidate.isoformat())

    if kind == "DAILY":
        return [
            (first + timedelta(days=i * step)).isoformat()
            for i in range(count)
        ]

    if kind == "WEEKLY":
        selected = sorted(weekdays[code] for code in parts[2].split(","))
        monday = first - timedelta(days=first.weekday())
        week_offset = 0
        while len(result) < count:
            for weekday in selected:
                add(monday + timedelta(days=week_offset + weekday))
                if len(result) == count:
                    return result
            week_offset += 7 * step

    elif kind == "MONTHLY":
        month_index = first.year * 12 + first.month - 1
        while len(result) < count:
            year, month_zero = divmod(month_index, 12)
            month = month_zero + 1
            last_day = monthrange(year, month)[1]

            if len(parts) == 3:
                requested = int(parts[2])
                day = last_day if requested == -1 else requested
            else:
                nth = int(parts[2])
                weekday = weekdays[parts[3]]
                if nth == -1:
                    day = last_day - (
                        date(year, month, last_day).weekday() - weekday
                    ) % 7
                else:
                    day = 1 + (
                        weekday - date(year, month, 1).weekday()
                    ) % 7 + 7 * (nth - 1)

            if day <= last_day:
                add(date(year, month, day))
            month_index += step

    elif kind == "YEARLY":
        month, day = map(int, parts[2].split("-"))
        year = first.year
        while len(result) < count:
            if day <= monthrange(year, month)[1]:
                add(date(year, month, day))
            year += step

    return result
