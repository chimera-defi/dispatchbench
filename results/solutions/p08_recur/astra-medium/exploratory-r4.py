from datetime import date, timedelta
from calendar import monthrange


def recur(start: str, rule: str, count: int) -> list[str]:
    first = date.fromisoformat(start)
    parts = rule.split()
    kind, step = parts[0], int(parts[1])
    weekdays = {wd: i for i, wd in enumerate(
        ("MO", "TU", "WE", "TH", "FR", "SA", "SU")
    )}
    result = []

    def add(candidate):
        if candidate >= first and len(result) < count:
            result.append(candidate.isoformat())

    if kind == "DAILY":
        return [
            (first + timedelta(days=i * step)).isoformat()
            for i in range(count)
        ]

    if kind == "WEEKLY":
        selected = sorted(weekdays[wd] for wd in parts[2].split(","))
        monday = first - timedelta(days=first.weekday())
        while len(result) < count:
            for wd in selected:
                add(monday + timedelta(days=wd))
            if len(result) < count:
                monday += timedelta(weeks=step)
        return result

    if kind == "MONTHLY":
        month_index = first.year * 12 + first.month - 1
        n = int(parts[2])

        while len(result) < count:
            year, month_zero = divmod(month_index, 12)
            month = month_zero + 1
            last_day = monthrange(year, month)[1]

            if len(parts) == 3:
                day = last_day if n == -1 else n
            else:
                wd = weekdays[parts[3]]
                if n == -1:
                    last_weekday = date(year, month, last_day).weekday()
                    day = last_day - (last_weekday - wd) % 7
                else:
                    first_weekday = date(year, month, 1).weekday()
                    day = 1 + (wd - first_weekday) % 7 + 7 * (n - 1)

            if day <= last_day:
                add(date(year, month, day))
            month_index += step

        return result

    month, day = map(int, parts[2].split("-"))
    year = first.year
    while len(result) < count:
        if day <= monthrange(year, month)[1]:
            add(date(year, month, day))
        year += step

    return result
