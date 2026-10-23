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
        week_zero = start_date - timedelta(days=start_date.weekday())
        active_week = 0

        while len(result) < count:
            week_start = week_zero + timedelta(weeks=active_week * interval)
            for weekday in weekdays:
                candidate = week_start + timedelta(days=weekday)
                if candidate >= start_date:
                    result.append(candidate.isoformat())
                    if len(result) == count:
                        break
            active_week += 1

        return result

    if frequency == "MONTHLY":
        start_month_index = start_date.year * 12 + start_date.month - 1
        active_month = 0

        if len(parts) == 3:
            requested_day = int(parts[2])

            while len(result) < count:
                month_index = start_month_index + active_month * interval
                year, month_zero_based = divmod(month_index, 12)
                month = month_zero_based + 1
                last_day = calendar.monthrange(year, month)[1]

                day = last_day if requested_day == -1 else requested_day
                if day <= last_day:
                    candidate = date(year, month, day)
                    if candidate >= start_date:
                        result.append(candidate.isoformat())

                active_month += 1

        else:
            occurrence = int(parts[2])
            weekday = weekday_numbers[parts[3]]

            while len(result) < count:
                month_index = start_month_index + active_month * interval
                year, month_zero_based = divmod(month_index, 12)
                month = month_zero_based + 1
                last_day = calendar.monthrange(year, month)[1]

                if occurrence == -1:
                    last_date = date(year, month, last_day)
                    day = last_day - (last_date.weekday() - weekday) % 7
                else:
                    first_date = date(year, month, 1)
                    day = (
                        1
                        + (weekday - first_date.weekday()) % 7
                        + 7 * (occurrence - 1)
                    )

                if day <= last_day:
                    candidate = date(year, month, day)
                    if candidate >= start_date:
                        result.append(candidate.isoformat())

                active_month += 1

        return result

    month, day = map(int, parts[2].split("-"))
    active_year = 0

    while len(result) < count:
        year = start_date.year + active_year * interval
        try:
            candidate = date(year, month, day)
        except ValueError:
            candidate = None

        if candidate is not None and candidate >= start_date:
            result.append(candidate.isoformat())

        active_year += 1

    return result
