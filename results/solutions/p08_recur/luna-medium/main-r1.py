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
        step = timedelta(days=interval)
        for _ in range(count):
            results.append(current.isoformat())
            current += step
        return results

    if kind == "WEEKLY":
        weekday_numbers = {
            "MO": 0, "TU": 1, "WE": 2, "TH": 3,
            "FR": 4, "SA": 5, "SU": 6,
        }
        weekdays = sorted(weekday_numbers[day] for day in parts[2].split(","))
        week_start = start_date - timedelta(days=start_date.weekday())
        week_index = 0

        while len(results) < count:
            active_start = week_start + timedelta(weeks=week_index)
            for weekday in weekdays:
                candidate = active_start + timedelta(days=weekday)
                if candidate >= start_date:
                    results.append(candidate.isoformat())
                    if len(results) == count:
                        return results
            week_index += interval

    if kind == "MONTHLY":
        month_index = 0
        day = parts[2]

        while len(results) < count:
            year, month = divmod(
                (start_date.year - 1) * 12 + start_date.month - 1
                + month_index * interval,
                12,
            )
            year += 1

            if len(parts) == 3:
                if day == "-1":
                    day_number = calendar.monthrange(year, month + 1)[1]
                else:
                    day_number = int(day)
                    if day_number > calendar.monthrange(year, month + 1)[1]:
                        month_index += 1
                        continue
            else:
                ordinal = int(day)
                weekday = {
                    "MO": 0, "TU": 1, "WE": 2, "TH": 3,
                    "FR": 4, "SA": 5, "SU": 6,
                }[parts[3]]
                days_in_month = calendar.monthrange(year, month + 1)[1]

                if ordinal == -1:
                    last_day = date(year, month + 1, days_in_month)
                    day_number = days_in_month - (
                        last_day.weekday() - weekday
                    ) % 7
                else:
                    first_day = date(year, month + 1, 1)
                    day_number = 1 + (weekday - first_day.weekday()) % 7 + 7 * (ordinal - 1)
                    if day_number > days_in_month:
                        month_index += 1
                        continue

            candidate = date(year, month + 1, day_number)
            if candidate >= start_date:
                results.append(candidate.isoformat())
            month_index += 1

        return results

    if kind == "YEARLY":
        month, day = map(int, parts[2].split("-"))
        year_offset = 0

        while len(results) < count:
            year = start_date.year + year_offset * interval
            try:
                candidate = date(year, month, day)
            except ValueError:
                year_offset += 1
                continue

            if candidate >= start_date:
                results.append(candidate.isoformat())
            year_offset += 1

        return results

    return results
