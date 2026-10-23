from datetime import date, timedelta
from calendar import monthrange


def recur(start: str, rule: str, count: int) -> list[str]:
    first = date.fromisoformat(start)
    parts = rule.split()
    kind, k = parts[0], int(parts[1])
    weekdays = {
        "MO": 0, "TU": 1, "WE": 2, "TH": 3,
        "FR": 4, "SA": 5, "SU": 6,
    }

    if kind == "DAILY":
        return [
            (first + timedelta(days=i * k)).isoformat()
            for i in range(count)
        ]

    result = []

    if kind == "WEEKLY":
        monday = first - timedelta(days=first.weekday())
        days = sorted(weekdays[wd] for wd in parts[2].split(","))
        week = 0

        while True:
            for wd in days:
                candidate = monday + timedelta(days=7 * week + wd)
                if candidate >= first:
                    result.append(candidate.isoformat())
                    if len(result) == count:
                        return result
            week += k

    if kind == "MONTHLY":
        month_index = first.year * 12 + first.month - 1
        n = int(parts[2])

        while len(result) < count:
            year, month_zero = divmod(month_index, 12)
            month = month_zero + 1
            first_weekday, last_day = monthrange(year, month)

            if len(parts) == 3:
                day = last_day if n == -1 else n
            else:
                wd = weekdays[parts[3]]
                if n == -1:
                    last_weekday = (first_weekday + last_day - 1) % 7
                    day = last_day - (last_weekday - wd) % 7
                else:
                    day = 1 + (wd - first_weekday) % 7 + 7 * (n - 1)

            if day <= last_day:
                candidate = date(year, month, day)
                if candidate >= first:
                    result.append(candidate.isoformat())

            month_index += k

        return result

    # YEARLY
    month, day = map(int, parts[2].split("-"))
    year = first.year

    while len(result) < count:
        if day <= monthrange(year, month)[1]:
            candidate = date(year, month, day)
            if candidate >= first:
                result.append(candidate.isoformat())
        year += k

    return result
