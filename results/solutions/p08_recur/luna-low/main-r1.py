from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    interval = int(parts[1])
    results = []

    if kind == "DAILY":
        current = start_date
        for _ in range(count):
            results.append(current.isoformat())
            current += timedelta(days=interval)
        return results

    if kind == "WEEKLY":
        weekdays = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                    "FR": 4, "SA": 5, "SU": 6}
        selected = sorted(weekdays[day] for day in parts[2].split(","))
        week_start = start_date - timedelta(days=start_date.weekday())
        week_index = 0

        while len(results) < count:
            if week_index % interval == 0:
                for weekday in selected:
                    current = week_start + timedelta(weeks=week_index, days=weekday)
                    if current >= start_date:
                        results.append(current.isoformat())
                        if len(results) == count:
                            break
            week_index += 1
        return results

    if kind == "MONTHLY":
        month_index = 0
        year, month = start_date.year, start_date.month

        while len(results) < count:
            if month_index % interval == 0:
                days_in_month = calendar.monthrange(year, month)[1]

                if len(parts) == 3:
                    day = int(parts[2])
                    if day == -1:
                        day = days_in_month
                    if 1 <= day <= days_in_month:
                        current = date(year, month, day)
                        if current >= start_date:
                            results.append(current.isoformat())
                else:
                    n = int(parts[2])
                    weekday = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                               "FR": 4, "SA": 5, "SU": 6}[parts[3]]
                    if n == -1:
                        day = days_in_month
                        while date(year, month, day).weekday() != weekday:
                            day -= 1
                    else:
                        first_weekday = date(year, month, 1).weekday()
                        day = 1 + (weekday - first_weekday) % 7 + 7 * (n - 1)
                        if day > days_in_month:
                            day = 0

                    if day:
                        current = date(year, month, day)
                        if current >= start_date:
                            results.append(current.isoformat())

            month_index += 1
            year, month = divmod(start_date.month - 1 + month_index, 12)
            year += start_date.year
            month += 1

        return results

    if kind == "YEARLY":
        month, day = map(int, parts[2].split("-"))
        year_index = 0
        while len(results) < count:
            year = start_date.year + year_index
            if year_index % interval == 0:
                try:
                    current = date(year, month, day)
                except ValueError:
                    current = None
                if current is not None and current >= start_date:
                    results.append(current.isoformat())
            year_index += interval
        return results
