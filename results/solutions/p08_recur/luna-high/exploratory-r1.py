from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    interval = int(parts[1])
    results = []

    def add(candidate):
        if candidate >= start_date:
            results.append(candidate.isoformat())

    if kind == "DAILY":
        current = start_date
        while len(results) < count:
            add(current)
            current += timedelta(days=interval)

    elif kind == "WEEKLY":
        weekdays = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                    "FR": 4, "SA": 5, "SU": 6}
        selected = sorted(weekdays[day] for day in parts[2].split(","))
        week_start = start_date - timedelta(days=start_date.weekday())
        week_index = 0

        while len(results) < count:
            active_start = week_start + timedelta(weeks=week_index * interval)
            for weekday in selected:
                candidate = active_start + timedelta(days=weekday)
                add(candidate)
                if len(results) == count:
                    break
            week_index += 1

    elif kind == "MONTHLY":
        month_index = 0
        while len(results) < count:
            month_number = start_date.month - 1 + month_index * interval
            year = start_date.year + month_number // 12
            month = month_number % 12 + 1
            last_day = calendar.monthrange(year, month)[1]

            if len(parts) == 3:
                day = int(parts[2])
                if day == -1:
                    day = last_day
                if 1 <= day <= last_day:
                    add(date(year, month, day))
            else:
                n = int(parts[2])
                weekday = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                           "FR": 4, "SA": 5, "SU": 6}[parts[3]]
                if n == -1:
                    candidate_day = last_day - (
                        date(year, month, last_day).weekday() - weekday
                    ) % 7
                else:
                    first_weekday = date(year, month, 1).weekday()
                    candidate_day = 1 + (weekday - first_weekday) % 7 + 7 * (n - 1)
                if candidate_day <= last_day:
                    add(date(year, month, candidate_day))

            month_index += 1

    elif kind == "YEARLY":
        month, day = map(int, parts[2].split("-"))
        year_index = 0
        while len(results) < count:
            year = start_date.year + year_index * interval
            try:
                add(date(year, month, day))
            except ValueError:
                pass
            year_index += 1

    return results
