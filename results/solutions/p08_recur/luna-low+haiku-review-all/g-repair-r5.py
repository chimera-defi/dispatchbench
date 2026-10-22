from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    interval = int(parts[1])
    results = []

    def add_if_valid(candidate):
        if candidate >= start_date:
            results.append(candidate.isoformat())

    if kind == "DAILY":
        current = start_date
        step = timedelta(days=interval)
        while len(results) < count:
            results.append(current.isoformat())
            current += step

    elif kind == "WEEKLY":
        weekdays = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}
        selected = sorted(weekdays[code] for code in parts[2].split(","))
        week_start = start_date - timedelta(days=start_date.weekday())
        week_index = 0

        while len(results) < count:
            active_start = week_start + timedelta(weeks=week_index * interval)
            for weekday in selected:
                candidate = active_start + timedelta(days=weekday)
                add_if_valid(candidate)
                if len(results) == count:
                    break
            week_index += 1

    elif kind == "MONTHLY":
        if len(parts) == 3:
            day_spec = int(parts[2])
            month_index = 0

            while len(results) < count:
                absolute_month = start_date.year * 12 + start_date.month - 1 + month_index * interval
                year, month_zero = divmod(absolute_month, 12)
                month = month_zero + 1
                last_day = calendar.monthrange(year, month)[1]
                day = last_day if day_spec == -1 else day_spec

                if day <= last_day:
                    add_if_valid(date(year, month, day))
                month_index += 1
        else:
            occurrence = int(parts[2])
            weekday = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}[parts[3]]
            month_index = 0

            while len(results) < count:
                absolute_month = start_date.year * 12 + start_date.month - 1 + month_index * interval
                year, month_zero = divmod(absolute_month, 12)
                month = month_zero + 1
                last_day = calendar.monthrange(year, month)[1]

                if occurrence == -1:
                    last_weekday = date(year, month, last_day).weekday()
                    day = last_day - (last_weekday - weekday) % 7
                else:
                    first_weekday = date(year, month, 1).weekday()
                    day = 1 + (weekday - first_weekday) % 7 + (occurrence - 1) * 7
                    if day > last_day:
                        day = None

                if day is not None:
                    add_if_valid(date(year, month, day))
                month_index += 1

    else:  # YEARLY
        month, day = map(int, parts[2].split("-"))
        year_index = 0

        while len(results) < count:
            year = start_date.year + year_index * interval
            try:
                candidate = date(year, month, day)
            except ValueError:
                candidate = None

            if candidate is not None:
                add_if_valid(candidate)
            year_index += 1

    return results
