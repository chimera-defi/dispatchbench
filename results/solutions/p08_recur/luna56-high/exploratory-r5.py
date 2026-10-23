from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]

    result = []

    if kind == "DAILY":
        step = int(parts[1])
        current = start_date
        for _ in range(count):
            result.append(current.isoformat())
            current += timedelta(days=step)
        return result

    if kind == "WEEKLY":
        step = int(parts[1])
        weekdays = sorted(
            {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
             "FR": 4, "SA": 5, "SU": 6}[x]
            for x in parts[2].split(",")
        )
        week_start = start_date - timedelta(days=start_date.weekday())
        week_index = 0

        while len(result) < count:
            active_start = week_start + timedelta(weeks=week_index * step)
            for weekday in weekdays:
                current = active_start + timedelta(days=weekday)
                if current >= start_date:
                    result.append(current.isoformat())
                    if len(result) == count:
                        break
            week_index += 1

        return result

    if kind == "MONTHLY":
        step = int(parts[1])
        month_index = 0

        while len(result) < count:
            total_months = start_date.year * 12 + start_date.month - 1
            total_months += month_index * step
            year, month_zero = divmod(total_months, 12)
            month = month_zero + 1

            if len(parts) == 3:
                day_spec = int(parts[2])
                if day_spec == -1:
                    day = calendar.monthrange(year, month)[1]
                else:
                    day = day_spec

                if day <= calendar.monthrange(year, month)[1]:
                    current = date(year, month, day)
                    if current >= start_date:
                        result.append(current.isoformat())
            else:
                n = int(parts[2])
                target_weekday = {
                    "MO": 0, "TU": 1, "WE": 2, "TH": 3,
                    "FR": 4, "SA": 5, "SU": 6
                }[parts[3]]

                last_day = calendar.monthrange(year, month)[1]
                if n == -1:
                    current = date(year, month, last_day)
                    current -= timedelta(days=(current.weekday() - target_weekday) % 7)
                else:
                    first = date(year, month, 1)
                    day = 1 + (target_weekday - first.weekday()) % 7 + (n - 1) * 7
                    current = date(year, month, day) if day <= last_day else None

                if current is not None and current >= start_date:
                    result.append(current.isoformat())

            month_index += 1

        return result

    if kind == "YEARLY":
        step = int(parts[1])
        month, day = map(int, parts[2].split("-"))
        year_index = 0

        while len(result) < count:
            year = start_date.year + year_index * step
            try:
                current = date(year, month, day)
            except ValueError:
                current = None

            if current is not None and current >= start_date:
                result.append(current.isoformat())

            year_index += 1

        return result

    raise ValueError("Invalid recurrence rule")
