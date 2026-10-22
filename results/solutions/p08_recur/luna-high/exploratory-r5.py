from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    k = int(parts[1])
    results = []

    if kind == "DAILY":
        current = start_date
        for _ in range(count):
            results.append(current.isoformat())
            current += timedelta(days=k)

    elif kind == "WEEKLY":
        weekday_codes = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
        weekdays = sorted(weekday_codes.index(code) for code in parts[2].split(","))
        week_start = start_date - timedelta(days=start_date.weekday())
        week = 0

        while len(results) < count:
            for weekday in weekdays:
                candidate = week_start + timedelta(weeks=week, days=weekday)
                if candidate >= start_date:
                    results.append(candidate.isoformat())
                    if len(results) == count:
                        break
            week += k

    elif kind == "MONTHLY":
        month_index = start_date.year * 12 + start_date.month - 1
        period = 0

        while len(results) < count:
            year, month0 = divmod(month_index + period, 12)
            month = month0 + 1
            days_in_month = calendar.monthrange(year, month)[1]

            if len(parts) == 3:
                day_rule = int(parts[2])
                day = days_in_month if day_rule == -1 else day_rule
                candidate = date(year, month, day) if day <= days_in_month else None
            else:
                occurrence = int(parts[2])
                target_weekday = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"].index(parts[3])
                first_weekday = calendar.monthrange(year, month)[0]

                if occurrence == -1:
                    day = days_in_month - (
                        (calendar.weekday(year, month, days_in_month) - target_weekday) % 7
                    )
                else:
                    day = 1 + (target_weekday - first_weekday) % 7 + 7 * (occurrence - 1)

                candidate = date(year, month, day) if day <= days_in_month else None

            if candidate is not None and candidate >= start_date:
                results.append(candidate.isoformat())
            period += k

    else:  # YEARLY
        month, day = map(int, parts[2].split("-"))
        year = start_date.year
        while len(results) < count:
            try:
                candidate = date(year, month, day)
            except ValueError:
                candidate = None

            if candidate is not None and candidate >= start_date:
                results.append(candidate.isoformat())
            year += k

    return results
