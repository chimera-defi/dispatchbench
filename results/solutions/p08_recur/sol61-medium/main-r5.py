from datetime import date, timedelta
from calendar import monthrange


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    kind, k = parts[0], int(parts[1])
    weekdays = {
        "MO": 0, "TU": 1, "WE": 2, "TH": 3,
        "FR": 4, "SA": 5, "SU": 6,
    }

    if kind == "DAILY":
        return [
            (start_date + timedelta(days=i * k)).isoformat()
            for i in range(count)
        ]

    result = []
    period = 0

    if kind == "WEEKLY":
        monday = start_date - timedelta(days=start_date.weekday())
        days = sorted(weekdays[wd] for wd in parts[2].split(","))

        while len(result) < count:
            week_start = monday + timedelta(weeks=period * k)
            for wd in days:
                candidate = week_start + timedelta(days=wd)
                if candidate >= start_date:
                    result.append(candidate.isoformat())
                    if len(result) == count:
                        return result
            period += 1

    elif kind == "MONTHLY":
        base_month = start_date.year * 12 + start_date.month - 1
        n = int(parts[2])

        while len(result) < count:
            year, month_index = divmod(base_month + period * k, 12)
            month = month_index + 1
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
                candidate = date(year, month, day)
                if candidate >= start_date:
                    result.append(candidate.isoformat())
            period += 1

    else:  # YEARLY
        month, day = map(int, parts[2].split("-"))

        while len(result) < count:
            year = start_date.year + period * k
            if day <= monthrange(year, month)[1]:
                candidate = date(year, month, day)
                if candidate >= start_date:
                    result.append(candidate.isoformat())
            period += 1

    return result
