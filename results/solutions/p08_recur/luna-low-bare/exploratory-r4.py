from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    interval = int(parts[1])
    results = []

    def add_if_valid(year, month, day):
        try:
            candidate = date(year, month, day)
        except ValueError:
            return
        if candidate >= start_date:
            results.append(candidate)

    if kind == "DAILY":
        for i in range(count):
            candidate = start_date + timedelta(days=i * interval)
            results.append(candidate)

    elif kind == "WEEKLY":
        weekdays = set(parts[2].split(","))
        weekday_map = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                       "FR": 4, "SA": 5, "SU": 6}
        active = {weekday_map[day] for day in weekdays}
        week_start = start_date - timedelta(days=start_date.weekday())
        week_index = 0
        while len(results) < count:
            if week_index % interval == 0:
                for weekday in sorted(active):
                    candidate = week_start + timedelta(
                        weeks=week_index, days=weekday
                    )
                    if candidate >= start_date:
                        results.append(candidate)
                        if len(results) == count:
                            break
            week_index += 1

    elif kind == "MONTHLY":
        if len(parts) == 3:
            day_spec = int(parts[2])
            month_index = 0
            while len(results) < count:
                total_month = start_date.year * 12 + start_date.month - 1
                total_month += month_index * interval
                year, month0 = divmod(total_month, 12)
                month = month0 + 1
                last_day = calendar.monthrange(year, month)[1]
                day = last_day if day_spec == -1 else day_spec
                if day <= last_day:
                    add_if_valid(year, month, day)
                month_index += 1
        else:
            nth = int(parts[2])
            weekday = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                       "FR": 4, "SA": 5, "SU": 6}[parts[3]]
            month_index = 0
            while len(results) < count:
                total_month = start_date.year * 12 + start_date.month - 1
                total_month += month_index * interval
                year, month0 = divmod(total_month, 12)
                month = month0 + 1
                month_cal = calendar.Calendar().monthdatescalendar(year, month)
                days = [
                    d for week in month_cal for d in week
                    if d.month == month and d.weekday() == weekday
                ]
                index = -1 if nth == -1 else nth - 1
                if -len(days) <= index < len(days):
                    candidate = days[index]
                    if candidate >= start_date:
                        results.append(candidate)
                month_index += 1

    elif kind == "YEARLY":
        month, day = map(int, parts[2].split("-"))
        year_index = 0
        while len(results) < count:
            year = start_date.year + year_index * interval
            add_if_valid(year, month, day)
            year_index += 1

    return [d.isoformat() for d in results]
