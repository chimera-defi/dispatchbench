from datetime import date, timedelta
from calendar import monthrange


def recur(start: str, rule: str, count: int) -> list[str]:
    first = date.fromisoformat(start)
    parts = rule.split()
    kind, k = parts[0], int(parts[1])
    weekdays = {wd: i for i, wd in enumerate(
        ("MO", "TU", "WE", "TH", "FR", "SA", "SU")
    )}

    if kind == "DAILY":
        return [
            (first + timedelta(days=i * k)).isoformat()
            for i in range(count)
        ]

    result = []

    if kind == "WEEKLY":
        days = sorted(weekdays[wd] for wd in parts[2].split(","))
        monday = first - timedelta(days=first.weekday())

        while True:
            for wd in days:
                candidate = monday + timedelta(days=wd)
                if candidate >= first:
                    result.append(candidate.isoformat())
                    if len(result) == count:
                        return result
            monday += timedelta(weeks=k)

    if kind == "MONTHLY":
        month_index = first.year * 12 + first.month - 1
        n = int(parts[2])
        target_wd = weekdays[parts[3]] if len(parts) == 4 else None

        while True:
            year, month_zero = divmod(month_index, 12)
            month = month_zero + 1
            first_wd, last_day = monthrange(year, month)

            if target_wd is None:
                day = last_day if n == -1 else n
            elif n == -1:
                last_wd = (first_wd + last_day - 1) % 7
                day = last_day - (last_wd - target_wd) % 7
            else:
                day = 1 + (target_wd - first_wd) % 7 + 7 * (n - 1)

            if day <= last_day:
                candidate = date(year, month, day)
                if candidate >= first:
                    result.append(candidate.isoformat())
                    if len(result) == count:
                        return result

            month_index += k

    # YEARLY
    month, day = map(int, parts[2].split("-"))
    year = first.year

    while True:
        if day <= monthrange(year, month)[1]:
            candidate = date(year, month, day)
            if candidate >= first:
                result.append(candidate.isoformat())
                if len(result) == count:
                    return result
        year += k
