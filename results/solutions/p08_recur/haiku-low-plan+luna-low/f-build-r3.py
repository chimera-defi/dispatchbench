from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    k = int(parts[1])
    result = []

    def emit(candidate):
        if candidate >= start_date:
            result.append(candidate.isoformat())

    if kind == "DAILY":
        step = timedelta(days=k)
        current = start_date
        while len(result) < count:
            result.append(current.isoformat())
            current += step
        return result

    if kind == "WEEKLY":
        weekday_codes = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                         "FR": 4, "SA": 5, "SU": 6}
        weekdays = sorted({weekday_codes[code] for code in parts[2].split(",")})
        monday = start_date - timedelta(days=start_date.weekday())
        week_index = 0

        while len(result) < count:
            week_start = monday + timedelta(days=7 * week_index)
            for weekday in weekdays:
                emit(week_start + timedelta(days=weekday))
                if len(result) == count:
                    return result
            week_index += k

    elif kind == "MONTHLY":
        y0, m0 = start_date.year, start_date.month
        month_index = 0

        if len(parts) == 3:
            day_number = int(parts[2])
            while len(result) < count:
                year, month = divmod(m0 - 1 + month_index, 12)
                year += y0
                month += 1
                last_day = calendar.monthrange(year, month)[1]
                day = last_day if day_number == -1 else day_number
                if day <= last_day:
                    emit(date(year, month, day))
                month_index += k
        else:
            n = int(parts[2])
            weekday_codes = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                             "FR": 4, "SA": 5, "SU": 6}
            weekday = weekday_codes[parts[3]]
            while len(result) < count:
                year, month = divmod(m0 - 1 + month_index, 12)
                year += y0
                month += 1
                first_weekday = date(year, month, 1).weekday()
                last_day = calendar.monthrange(year, month)[1]

                if n == -1:
                    candidate_day = last_day - (
                        (date(year, month, last_day).weekday() - weekday) % 7
                    )
                else:
                    candidate_day = 1 + ((weekday - first_weekday) % 7) + 7 * (n - 1)

                if candidate_day <= last_day:
                    emit(date(year, month, candidate_day))
                month_index += k

    elif kind == "YEARLY":
        month, day = map(int, parts[2].split("-"))
        year_index = 0
        while len(result) < count:
            year = start_date.year + year_index
            try:
                emit(date(year, month, day))
            except ValueError:
                pass
            year_index += k

    return result
