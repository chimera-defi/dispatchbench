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

    weekday_codes = {
        "MO": 0, "TU": 1, "WE": 2, "TH": 3,
        "FR": 4, "SA": 5, "SU": 6,
    }

    if kind == "WEEKLY":
        weekdays = sorted(weekday_codes[code] for code in parts[2].split(","))
        week_start = start_date - timedelta(days=start_date.weekday())
        week_index = 0
        while len(results) < count:
            monday = week_start + timedelta(weeks=week_index)
            for weekday in weekdays:
                current = monday + timedelta(days=weekday)
                if current >= start_date:
                    results.append(current.isoformat())
                    if len(results) == count:
                        break
            week_index += interval
        return results

    if kind == "MONTHLY":
        month_index = 0
        while len(results) < count:
            year, month0 = divmod(start_date.month - 1 + month_index, 12)
            year += start_date.year
            month = month0 + 1
            if year >= 3000:
                break

            last_day = calendar.monthrange(year, month)[1]
            if len(parts) == 3:
                day = int(parts[2])
                if day == -1:
                    day = last_day
                if 1 <= day <= last_day:
                    current = date(year, month, day)
                    if current >= start_date:
                        results.append(current.isoformat())
            else:
                n = int(parts[2])
                weekday = weekday_codes[parts[3]]
                if n == -1:
                    day = last_day - (
                        date(year, month, last_day).weekday() - weekday
                    ) % 7
                else:
                    first_day = date(year, month, 1)
                    day = 1 + (weekday - first_day.weekday()) % 7 + 7 * (n - 1)
                if day <= last_day:
                    current = date(year, month, day)
                    if current >= start_date:
                        results.append(current.isoformat())

            month_index += interval
        return results

    if kind == "YEARLY":
        month, day = map(int, parts[2].split("-"))
        year_index = 0
        while len(results) < count:
            year = start_date.year + year_index
            if year >= 3000:
                break
            try:
                current = date(year, month, day)
            except ValueError:
                current = None
            if current is not None and current >= start_date:
                results.append(current.isoformat())
            year_index += interval
        return results

    return results
