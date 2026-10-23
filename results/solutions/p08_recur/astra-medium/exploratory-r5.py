from calendar import monthrange
from datetime import date, timedelta


def recur(start: str, rule: str, count: int) -> list[str]:
    first = date.fromisoformat(start)
    tokens = rule.split()
    kind = tokens[0]
    k = int(tokens[1])
    weekdays = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                "FR": 4, "SA": 5, "SU": 6}

    if kind == "DAILY":
        return [
            (first + timedelta(days=i * k)).isoformat()
            for i in range(count)
        ]

    if kind == "WEEKLY":
        monday = first - timedelta(days=first.weekday())
        selected = sorted(weekdays[wd] for wd in tokens[2].split(","))
    elif kind == "MONTHLY":
        initial_month = first.year * 12 + first.month - 1
        n = int(tokens[2])
        target_weekday = weekdays[tokens[3]] if len(tokens) == 4 else None
    else:
        month, day = map(int, tokens[2].split("-"))

    result = []
    offset = 0

    while True:
        candidates = []

        if kind == "WEEKLY":
            week_start = monday + timedelta(weeks=offset)
            candidates = [
                week_start + timedelta(days=wd) for wd in selected
            ]

        elif kind == "MONTHLY":
            year, month_index = divmod(initial_month + offset, 12)
            month = month_index + 1
            first_weekday, last_day = monthrange(year, month)

            if target_weekday is None:
                day = last_day if n == -1 else n
            elif n == -1:
                last_weekday = (first_weekday + last_day - 1) % 7
                day = last_day - (last_weekday - target_weekday) % 7
            else:
                day = 1 + (target_weekday - first_weekday) % 7 + 7 * (n - 1)

            if day <= last_day:
                candidates.append(date(year, month, day))

        else:
            year = first.year + offset
            if day <= monthrange(year, month)[1]:
                candidates.append(date(year, month, day))

        for candidate in candidates:
            if candidate >= first:
                result.append(candidate.isoformat())
                if len(result) == count:
                    return result

        offset += k
