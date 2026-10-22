from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    result = []

    if kind == "DAILY":
        step = int(parts[1])
        current = start_date
        while len(result) < count and current.year < 3000:
            result.append(current.isoformat())
            current += timedelta(days=step)

    elif kind == "WEEKLY":
        step = int(parts[1])
        weekday_num = {
            "MO": 0, "TU": 1, "WE": 2, "TH": 3,
            "FR": 4, "SA": 5, "SU": 6,
        }
        weekdays = sorted(weekday_num[day] for day in parts[2].split(","))
        monday = start_date - timedelta(days=start_date.weekday())
        week_index = 0

        while len(result) < count:
            week_start = monday + timedelta(weeks=week_index)
            if week_start.year >= 3000:
                break
            for weekday in weekdays:
                candidate = week_start + timedelta(days=weekday)
                if candidate >= start_date:
                    result.append(candidate.isoformat())
                    if len(result) == count:
                        break
            week_index += step

    elif kind == "MONTHLY":
        step = int(parts[1])
        base_index = start_date.year * 12 + start_date.month - 1
        offset = 0

        while len(result) < count:
            year, month0 = divmod(base_index + offset, 12)
            if year >= 3000:
                break
            month = month0 + 1
            month_length = calendar.monthrange(year, month)[1]

            if len(parts) == 3:
                day = int(parts[2])
                if day == -1:
                    day = month_length
                if day <= month_length:
                    candidate = date(year, month, day)
                    if candidate >= start_date:
                        result.append(candidate.isoformat())
            else:
                n = int(parts[2])
                weekday = {
                    "MO": 0, "TU": 1, "WE": 2, "TH": 3,
                    "FR": 4, "SA": 5, "SU": 6,
                }[parts[3]]
                if n == -1:
                    last = date(year, month, month_length)
                    day = month_length - (last.weekday() - weekday) % 7
                else:
                    first = date(year, month, 1)
                    day = 1 + (weekday - first.weekday()) % 7 + 7 * (n - 1)

                if day <= month_length:
                    candidate = date(year, month, day)
                    if candidate >= start_date:
                        result.append(candidate.isoformat())

            offset += step

    elif kind == "YEARLY":
        step = int(parts[1])
        month, day = map(int, parts[2].split("-"))
        year = start_date.year

        while len(result) < count and year < 3000:
            try:
                candidate = date(year, month, day)
                if candidate >= start_date:
                    result.append(candidate.isoformat())
            except ValueError:
                pass
            year += step

    return result
