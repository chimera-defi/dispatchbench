from datetime import date, timedelta
from calendar import monthrange


def recur(start: str, rule: str, count: int) -> list[str]:
    first = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    k = int(parts[1])
    weekdays = {
        "MO": 0, "TU": 1, "WE": 2, "TH": 3,
        "FR": 4, "SA": 5, "SU": 6,
    }
    result = []

    if kind == "DAILY":
        return [
            (first + timedelta(days=i * k)).isoformat()
            for i in range(count)
        ]

    if kind == "WEEKLY":
        monday = first - timedelta(days=first.weekday())
        selected = sorted(weekdays[wd] for wd in parts[2].split(","))
        offset = 0

        while len(result) < count:
            for wd in selected:
                candidate = monday + timedelta(days=offset + wd)
                if candidate >= first:
                    result.append(candidate.isoformat())
                    if len(result) == count:
                        return result
            offset += 7 * k

    elif kind == "MONTHLY":
        month_index = first.year * 12 + first.month - 1
        n = int(parts[2])

        while len(result) < count:
            year, month_zero = divmod(month_index, 12)
            month = month_zero + 1
            first_weekday, days_in_month = monthrange(year, month)

            if len(parts) == 3:
                day = days_in_month if n == -1 else n
            else:
                wd = weekdays[parts[3]]
                if n == -1:
                    last_weekday = (first_weekday + days_in_month - 1) % 7
                    day = days_in_month - (last_weekday - wd) % 7
                else:
                    day = 1 + (wd - first_weekday) % 7 + 7 * (n - 1)

            if day <= days_in_month:
                candidate = date(year, month, day)
                if candidate >= first:
                    result.append(candidate.isoformat())

            month_index += k

    elif kind == "YEARLY":
        month, day = map(int, parts[2].split("-"))
        year = first.year

        while len(result) < count:
            if day <= monthrange(year, month)[1]:
                candidate = date(year, month, day)
                if candidate >= first:
                    result.append(candidate.isoformat())
            year += k

    return result
