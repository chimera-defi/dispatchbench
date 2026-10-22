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
        while len(result) < count:
            result.append(current.isoformat())
            current += timedelta(days=step)

    elif kind == "WEEKLY":
        step = int(parts[1])
        weekdays = sorted(("MO", "TU", "WE", "TH", "FR", "SA", "SU").index(
            code
        ) for code in parts[2].split(","))
        week_start = start_date - timedelta(days=start_date.weekday())
        week = 0
        while len(result) < count:
            monday = week_start + timedelta(weeks=week)
            for weekday in weekdays:
                current = monday + timedelta(days=weekday)
                if current >= start_date:
                    result.append(current.isoformat())
                    if len(result) == count:
                        break
            week += step

    elif kind == "MONTHLY":
        step = int(parts[1])
        month_index = start_date.year * 12 + start_date.month - 1
        if len(parts) == 3:
            day_spec = int(parts[2])
            weekday_spec = None
        else:
            day_spec = int(parts[2])
            weekday_spec = ("MO", "TU", "WE", "TH", "FR", "SA", "SU").index(parts[3])

        while len(result) < count:
            year, month0 = divmod(month_index, 12)
            month = month0 + 1
            days_in_month = calendar.monthrange(year, month)[1]

            if weekday_spec is None:
                day = days_in_month if day_spec == -1 else day_spec
                if day <= days_in_month:
                    current = date(year, month, day)
                    if current >= start_date:
                        result.append(current.isoformat())
            elif day_spec == -1:
                last_weekday = date(year, month, days_in_month).weekday()
                day = days_in_month - (last_weekday - weekday_spec) % 7
                current = date(year, month, day)
                if current >= start_date:
                    result.append(current.isoformat())
            else:
                first_weekday = date(year, month, 1).weekday()
                day = 1 + (weekday_spec - first_weekday) % 7 + 7 * (day_spec - 1)
                if day <= days_in_month:
                    current = date(year, month, day)
                    if current >= start_date:
                        result.append(current.isoformat())

            month_index += step

    else:  # YEARLY
        step = int(parts[1])
        month, day = map(int, parts[2].split("-"))
        year = start_date.year
        while len(result) < count:
            if day <= calendar.monthrange(year, month)[1]:
                current = date(year, month, day)
                if current >= start_date:
                    result.append(current.isoformat())
            year += step

    return result
