from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    first = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    interval = int(parts[1])
    result = []

    def add(candidate):
        if candidate is not None and candidate >= first:
            result.append(candidate.isoformat())

    if kind == "DAILY":
        current = first
        while len(result) < count:
            add(current)
            current += timedelta(days=interval)
        return result

    if kind == "WEEKLY":
        weekdays = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                    "FR": 4, "SA": 5, "SU": 6}
        selected = sorted(weekdays[code] for code in parts[2].split(","))
        week_start = first - timedelta(days=first.weekday())
        week_index = 0
        while len(result) < count:
            active_start = week_start + timedelta(weeks=week_index)
            for weekday in selected:
                add(active_start + timedelta(days=weekday))
                if len(result) == count:
                    break
            week_index += interval
        return result

    if kind == "MONTHLY":
        if len(parts) == 3:
            day_spec = int(parts[2])
            nth_weekday = None
        else:
            day_spec = None
            nth_weekday = (int(parts[2]), {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                                           "FR": 4, "SA": 5, "SU": 6}[parts[3]])

        month_index = 0
        while len(result) < count:
            total_month = (first.year - 1) * 12 + (first.month - 1) + month_index
            year, month0 = divmod(total_month, 12)
            year += 1
            month = month0 + 1
            last_day = calendar.monthrange(year, month)[1]

            if day_spec is not None:
                day = last_day if day_spec == -1 else day_spec
                candidate = date(year, month, day) if day <= last_day else None
            else:
                n, weekday = nth_weekday
                if n == -1:
                    last_weekday = date(year, month, last_day).weekday()
                    day = last_day - (last_weekday - weekday) % 7
                    candidate = date(year, month, day)
                else:
                    first_weekday = date(year, month, 1).weekday()
                    day = 1 + (weekday - first_weekday) % 7 + 7 * (n - 1)
                    candidate = date(year, month, day) if day <= last_day else None

            add(candidate)
            month_index += interval

        return result

    # YEARLY
    month, day = map(int, parts[2].split("-"))
    year_offset = 0
    while len(result) < count:
        year = first.year + year_offset
        try:
            candidate = date(year, month, day)
        except ValueError:
            candidate = None
        add(candidate)
        year_offset += interval

    return result
