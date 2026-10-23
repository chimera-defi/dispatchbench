from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    frequency = parts[0]
    interval = int(parts[1])
    results = []

    if frequency == "DAILY":
        return [
            (start_date + timedelta(days=i * interval)).isoformat()
            for i in range(count)
        ]

    weekdays = {
        "MO": 0, "TU": 1, "WE": 2, "TH": 3,
        "FR": 4, "SA": 5, "SU": 6,
    }

    if frequency == "WEEKLY":
        selected_days = sorted(weekdays[code] for code in parts[2].split(","))
        week_zero = start_date - timedelta(days=start_date.weekday())
        active_week = 0

        while len(results) < count:
            week_start = week_zero + timedelta(weeks=active_week * interval)
            for weekday in selected_days:
                candidate = week_start + timedelta(days=weekday)
                if candidate >= start_date:
                    results.append(candidate.isoformat())
                    if len(results) == count:
                        return results
            active_week += 1

    if frequency == "MONTHLY":
        start_month_index = start_date.year * 12 + start_date.month - 1
        active_month = 0

        while len(results) < count:
            month_index = start_month_index + active_month * interval
            year, month_zero = divmod(month_index, 12)
            month = month_zero + 1
            days_in_month = calendar.monthrange(year, month)[1]
            candidate = None

            if len(parts) == 3:
                requested_day = int(parts[2])
                day = days_in_month if requested_day == -1 else requested_day
                if day <= days_in_month:
                    candidate = date(year, month, day)
            else:
                occurrence = int(parts[2])
                target_weekday = weekdays[parts[3]]

                if occurrence == -1:
                    last_date = date(year, month, days_in_month)
                    day = days_in_month - (
                        last_date.weekday() - target_weekday
                    ) % 7
                    candidate = date(year, month, day)
                else:
                    first_weekday = date(year, month, 1).weekday()
                    day = (
                        1
                        + (target_weekday - first_weekday) % 7
                        + 7 * (occurrence - 1)
                    )
                    if day <= days_in_month:
                        candidate = date(year, month, day)

            if candidate is not None and candidate >= start_date:
                results.append(candidate.isoformat())

            active_month += 1

        return results

    month, day = map(int, parts[2].split("-"))
    active_year = 0

    while len(results) < count:
        year = start_date.year + active_year * interval
        try:
            candidate = date(year, month, day)
        except ValueError:
            candidate = None

        if candidate is not None and candidate >= start_date:
            results.append(candidate.isoformat())

        active_year += 1

    return results
