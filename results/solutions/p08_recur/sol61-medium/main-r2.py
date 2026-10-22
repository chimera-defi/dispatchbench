from datetime import date, timedelta
from calendar import monthrange


def recur(start: str, rule: str, count: int) -> list[str]:
    first = date.fromisoformat(start)
    parts = rule.split()
    frequency = parts[0]
    k = int(parts[1])
    weekdays = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                "FR": 4, "SA": 5, "SU": 6}

    if frequency == "DAILY":
        return [
            (first + timedelta(days=i * k)).isoformat()
            for i in range(count)
        ]

    result = []

    if frequency == "WEEKLY":
        days = sorted(weekdays[wd] for wd in parts[2].split(","))
        monday = first - timedelta(days=first.weekday())

        while True:
            for day in days:
                candidate = monday + timedelta(days=day)
                if candidate >= first:
                    result.append(candidate.isoformat())
                    if len(result) == count:
                        return result
            monday += timedelta(weeks=k)

    if frequency == "MONTHLY":
        month_index = first.year * 12 + first.month - 1

        while True:
            year, month_zero = divmod(month_index, 12)
            month = month_zero + 1
            last_day = monthrange(year, month)[1]

            if len(parts) == 3:
                requested_day = int(parts[2])
                day = last_day if requested_day == -1 else requested_day
            else:
                n = int(parts[2])
                weekday = weekdays[parts[3]]
                if n == -1:
                    day = last_day - (
                        date(year, month, last_day).weekday() - weekday
                    ) % 7
                else:
                    day = (
                        1
                        + (weekday - date(year, month, 1).weekday()) % 7
                        + 7 * (n - 1)
                    )

            if day <= last_day:
                candidate = date(year, month, day)
                if candidate >= first:
                    result.append(candidate.isoformat())
                    if len(result) == count:
                        return result

            month_index += k

    if frequency == "YEARLY":
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
