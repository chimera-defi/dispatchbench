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
        weekdays = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}
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
        while len(results) < count:
            year = start_date.year + (start_date.month - 1 + month_index) // 12
            month = (start_date.month - 1 + month_index) % 12 + 1
            _, last_day = calendar.monthrange(year, month)

            if month_index % interval == 0:
                if len(parts) == 3:
                    day_spec = int(parts[2])
                    day = last_day if day_spec == -1 else day_spec
                    if day <= last_day:
                        current = date(year, month, day)
                        if current >= start_date:
                            results.append(current.isoformat())
                else:
                    ordinal = int(parts[2])
                    weekday = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}[parts[3]]
                    if ordinal == -1:
                        day = last_day - ((date(year, month, last_day).weekday() - weekday) % 7)
                    else:
                        first_weekday = date(year, month, 1).weekday()
                        day = 1 + (weekday - first_weekday) % 7 + 7 * (ordinal - 1)
                    if day <= last_day:
                        current = date(year, month, day)
                        if current >= start_date:
                            results.append(current.isoformat())

            month_index += 1
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
            year_index += 1
        return results

    return results
