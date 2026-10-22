from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    result = []

    def add(candidate):
        if candidate >= start_date:
            result.append(candidate.isoformat())

    if kind == "DAILY":
        step = int(parts[1])
        current = start_date
        while len(result) < count and current.year < 3000:
            add(current)
            current += timedelta(days=step)

    elif kind == "WEEKLY":
        step = int(parts[1])
        weekday_codes = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                         "FR": 4, "SA": 5, "SU": 6}
        weekdays = sorted(weekday_codes[code] for code in parts[2].split(","))
        monday = start_date - timedelta(days=start_date.weekday())
        week_offset = 0

        while len(result) < count:
            week_start = monday + timedelta(weeks=week_offset)
            if week_start.year >= 3000:
                break
            for weekday in weekdays:
                candidate = week_start + timedelta(days=weekday)
                add(candidate)
                if len(result) == count:
                    break
            week_offset += step

    elif kind == "MONTHLY":
        step = int(parts[1])
        month_index = start_date.year * 12 + start_date.month - 1

        while len(result) < count:
            year, month_zero = divmod(month_index, 12)
            if year >= 3000:
                break
            month = month_zero + 1
            days_in_month = calendar.monthrange(year, month)[1]

            if len(parts) == 3:
                day = int(parts[2])
                if day == -1:
                    day = days_in_month
                if day <= days_in_month:
                    add(date(year, month, day))
            else:
                occurrence = int(parts[2])
                weekday_codes = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                                 "FR": 4, "SA": 5, "SU": 6}
                weekday = weekday_codes[parts[3]]

                if occurrence == -1:
                    last_day = date(year, month, days_in_month)
                    day = days_in_month - (last_day.weekday() - weekday) % 7
                    add(date(year, month, day))
                else:
                    first_day = date(year, month, 1)
                    day = 1 + (weekday - first_day.weekday()) % 7 + 7 * (occurrence - 1)
                    if day <= days_in_month:
                        add(date(year, month, day))

            month_index += step

    elif kind == "YEARLY":
        step = int(parts[1])
        month, day = map(int, parts[2].split("-"))
        year = start_date.year

        while len(result) < count and year < 3000:
            try:
                add(date(year, month, day))
            except ValueError:
                pass
            year += step

    return result
