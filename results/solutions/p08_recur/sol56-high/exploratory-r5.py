from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    frequency = parts[0]
    interval = int(parts[1])
    result = []

    if frequency == "DAILY":
        return [
            (start_date + timedelta(days=i * interval)).isoformat()
            for i in range(count)
        ]

    weekday_numbers = {
        "MO": 0,
        "TU": 1,
        "WE": 2,
        "TH": 3,
        "FR": 4,
        "SA": 5,
        "SU": 6,
    }

    if frequency == "WEEKLY":
        weekdays = sorted(weekday_numbers[code] for code in parts[2].split(","))
        week_start = start_date - timedelta(days=start_date.weekday())
        period = 0

        while len(result) < count:
            active_week = week_start + timedelta(weeks=period * interval)
            for weekday in weekdays:
                candidate = active_week + timedelta(days=weekday)
                if candidate >= start_date:
                    result.append(candidate.isoformat())
                    if len(result) == count:
                        break
            period += 1

        return result

    if frequency == "MONTHLY":
        period = 0

        while len(result) < count:
            month_index = (
                start_date.year * 12
                + start_date.month - 1
                + period * interval
            )
            year, zero_based_month = divmod(month_index, 12)
            month = zero_based_month + 1
            last_day = calendar.monthrange(year, month)[1]
            candidate = None

            if len(parts) == 3:
                day_spec = int(parts[2])
                day = last_day if day_spec == -1 else day_spec
                if day <= last_day:
                    candidate = date(year, month, day)
            else:
                occurrence = int(parts[2])
                target_weekday = weekday_numbers[parts[3]]

                if occurrence == -1:
                    last_date = date(year, month, last_day)
                    day = last_day - (
                        last_date.weekday() - target_weekday
                    ) % 7
                    candidate = date(year, month, day)
                else:
                    first_date = date(year, month, 1)
                    day = (
                        1
                        + (target_weekday - first_date.weekday()) % 7
                        + 7 * (occurrence - 1)
                    )
                    if day <= last_day:
                        candidate = date(year, month, day)

            if candidate is not None and candidate >= start_date:
                result.append(candidate.isoformat())

            period += 1

        return result

    month, day = map(int, parts[2].split("-"))
    period = 0

    while len(result) < count:
        year = start_date.year + period * interval
        try:
            candidate = date(year, month, day)
        except ValueError:
            candidate = None

        if candidate is not None and candidate >= start_date:
            result.append(candidate.isoformat())

        period += 1

    return result
