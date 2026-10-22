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
        weekdays = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                    "FR": 4, "SA": 5, "SU": 6}
        selected = {weekdays[day] for day in parts[2].split(",")}
        week_start = start_date - timedelta(days=start_date.weekday())
        week_index = 0

        while len(result) < count:
            if week_index % step == 0:
                for weekday in sorted(selected):
                    current = week_start + timedelta(days=weekday)
                    if current >= start_date:
                        result.append(current.isoformat())
                        if len(result) == count:
                            break
            week_index += 1
            week_start += timedelta(days=7)

    elif kind == "MONTHLY":
        step = int(parts[1])
        month_index = 0
        year, month = start_date.year, start_date.month

        while len(result) < count:
            if month_index % step == 0:
                last_day = calendar.monthrange(year, month)[1]
                if len(parts) == 3:
                    day = int(parts[2])
                    day = last_day if day == -1 else day
                    if day <= last_day:
                        current = date(year, month, day)
                        if current >= start_date:
                            result.append(current.isoformat())
                else:
                    occurrence = int(parts[2])
                    weekday = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                               "FR": 4, "SA": 5, "SU": 6}[parts[3]]
                    if occurrence == -1:
                        day = last_day - (
                            date(year, month, last_day).weekday() - weekday
                        ) % 7
                    else:
                        first_weekday = date(year, month, 1).weekday()
                        day = 1 + (weekday - first_weekday) % 7 + 7 * (occurrence - 1)
                    if day <= last_day:
                        current = date(year, month, day)
                        if current >= start_date:
                            result.append(current.isoformat())

            month_index += 1
            month += step
            year += (month - 1) // 12
            month = (month - 1) % 12 + 1

    else:  # YEARLY
        step = int(parts[1])
        target_month, target_day = map(int, parts[2].split("-"))
        year = start_date.year
        year_index = 0

        while len(result) < count:
            if year_index % step == 0:
                try:
                    current = date(year, target_month, target_day)
                except ValueError:
                    current = None
                if current is not None and current >= start_date:
                    result.append(current.isoformat())
            year_index += 1
            year += step

    return result
