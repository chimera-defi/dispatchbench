from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    interval = int(parts[1])
    result = []

    def formatted(d: date) -> str:
        return f"{d.year:04d}-{d.month:02d}-{d.day:02d}"

    if kind == "DAILY":
        current = start_date
        for _ in range(count):
            result.append(formatted(current))
            current += timedelta(days=interval)
        return result

    if kind == "WEEKLY":
        weekdays = parts[2].split(",")
        weekday_numbers = sorted(
            {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}[day]
            for day in weekdays
        )
        week_start = start_date - timedelta(days=start_date.weekday())
        week_index = 0

        while len(result) < count:
            active_week = week_start + timedelta(weeks=week_index)
            for weekday in weekday_numbers:
                candidate = active_week + timedelta(days=weekday)
                if candidate >= start_date:
                    result.append(formatted(candidate))
                    if len(result) == count:
                        break
            week_index += interval
        return result

    if kind == "MONTHLY":
        month_index = 0

        if len(parts) == 3:
            day_of_month = int(parts[2])
            while len(result) < count:
                year = start_date.year + (start_date.month - 1 + month_index) // 12
                month = (start_date.month - 1 + month_index) % 12 + 1
                last_day = calendar.monthrange(year, month)[1]
                day = last_day if day_of_month == -1 else day_of_month

                if day <= last_day:
                    candidate = date(year, month, day)
                    if candidate >= start_date:
                        result.append(formatted(candidate))
                month_index += interval
        else:
            occurrence = int(parts[2])
            weekday = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}[parts[3]]

            while len(result) < count:
                year = start_date.year + (start_date.month - 1 + month_index) // 12
                month = (start_date.month - 1 + month_index) % 12 + 1
                last_day = calendar.monthrange(year, month)[1]

                if occurrence == -1:
                    day = last_day - (date(year, month, last_day).weekday() - weekday) % 7
                else:
                    first_weekday = date(year, month, 1).weekday()
                    day = 1 + (weekday - first_weekday) % 7 + 7 * (occurrence - 1)

                if day <= last_day:
                    candidate = date(year, month, day)
                    if candidate >= start_date:
                        result.append(formatted(candidate))
                month_index += interval
        return result

    if kind == "YEARLY":
        month, day = map(int, parts[2].split("-"))
        year_index = 0

        while len(result) < count:
            year = start_date.year + year_index
            try:
                candidate = date(year, month, day)
            except ValueError:
                candidate = None

            if candidate is not None and candidate >= start_date:
                result.append(formatted(candidate))
            year_index += interval

        return result
