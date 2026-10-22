from datetime import date, timedelta
from calendar import monthrange


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    frequency, step = parts[0], int(parts[1])
    weekdays = {name: i for i, name in enumerate(
        ("MO", "TU", "WE", "TH", "FR", "SA", "SU")
    )}
    result = []

    if frequency == "DAILY":
        return [
            (start_date + timedelta(days=i * step)).isoformat()
            for i in range(count)
        ]

    if frequency == "WEEKLY":
        selected = sorted(weekdays[name] for name in parts[2].split(","))
        monday = start_date - timedelta(days=start_date.weekday())
        while len(result) < count:
            for weekday in selected:
                candidate = monday + timedelta(days=weekday)
                if candidate >= start_date:
                    result.append(candidate.isoformat())
                    if len(result) == count:
                        return result
            monday += timedelta(weeks=step)

    elif frequency == "MONTHLY":
        month_index = start_date.year * 12 + start_date.month - 1
        while len(result) < count:
            year, month_zero = divmod(month_index, 12)
            month = month_zero + 1
            first_weekday, last_day = monthrange(year, month)

            if len(parts) == 3:
                requested_day = int(parts[2])
                day = last_day if requested_day == -1 else requested_day
            else:
                occurrence = int(parts[2])
                weekday = weekdays[parts[3]]
                if occurrence == -1:
                    last_weekday = (first_weekday + last_day - 1) % 7
                    day = last_day - (last_weekday - weekday) % 7
                else:
                    day = (
                        1 + (weekday - first_weekday) % 7
                        + 7 * (occurrence - 1)
                    )

            if day <= last_day:
                candidate = date(year, month, day)
                if candidate >= start_date:
                    result.append(candidate.isoformat())
            month_index += step

    elif frequency == "YEARLY":
        month, day = map(int, parts[2].split("-"))
        year = start_date.year
        while len(result) < count:
            if day <= monthrange(year, month)[1]:
                candidate = date(year, month, day)
                if candidate >= start_date:
                    result.append(candidate.isoformat())
            year += step

    return result
