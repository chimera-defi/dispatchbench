from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    result = []

    if kind == "DAILY":
        step = int(parts[1])
        for i in range(count):
            result.append((start_date + timedelta(days=i * step)).isoformat())
        return result

    if kind == "WEEKLY":
        step = int(parts[1])
        weekdays = sorted(
            ["MO", "TU", "WE", "TH", "FR", "SA", "SU"].index(day)
            for day in parts[2].split(",")
        )
        week_start = start_date - timedelta(days=start_date.weekday())
        week_index = 0

        while len(result) < count:
            current_week = week_start + timedelta(days=week_index * step * 7)
            for weekday in weekdays:
                candidate = current_week + timedelta(days=weekday)
                if candidate >= start_date:
                    result.append(candidate.isoformat())
                    if len(result) == count:
                        return result
            week_index += 1
        return result

    if kind == "MONTHLY":
        step = int(parts[1])
        start_month_index = start_date.year * 12 + (start_date.month - 1)
        offset = 0

        while len(result) < count:
            month_index = start_month_index + offset * step
            year, month_zero = divmod(month_index, 12)
            month = month_zero + 1
            days_in_month = calendar.monthrange(year, month)[1]

            if len(parts) == 3:
                day_spec = int(parts[2])
                day = days_in_month if day_spec == -1 else day_spec
                if day <= days_in_month:
                    candidate = date(year, month, day)
                    if candidate >= start_date:
                        result.append(candidate.isoformat())
            else:
                n = int(parts[2])
                weekday = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"].index(parts[3])
                first_weekday = date(year, month, 1).weekday()

                if n == -1:
                    last = date(year, month, days_in_month)
                    day = days_in_month - ((last.weekday() - weekday) % 7)
                else:
                    day = 1 + ((weekday - first_weekday) % 7) + 7 * (n - 1)

                if day <= days_in_month:
                    candidate = date(year, month, day)
                    if candidate >= start_date:
                        result.append(candidate.isoformat())

            offset += 1

        return result

    if kind == "YEARLY":
        step = int(parts[1])
        month, day = map(int, parts[2].split("-"))
        year_offset = 0

        while len(result) < count:
            year = start_date.year + year_offset * step
            try:
                candidate = date(year, month, day)
            except ValueError:
                candidate = None

            if candidate is not None and candidate >= start_date:
                result.append(candidate.isoformat())

            year_offset += 1

        return result

    raise ValueError("Invalid recurrence rule")
