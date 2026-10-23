from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    results = []

    if kind == "DAILY":
        step = int(parts[1])
        for i in range(count):
            d = start_date + timedelta(days=i * step)
            results.append(d.isoformat())
        return results

    if kind == "WEEKLY":
        step = int(parts[1])
        weekdays = sorted(
            {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
             "FR": 4, "SA": 5, "SU": 6}[x]
            for x in parts[2].split(",")
        )
        week_start = start_date - timedelta(days=start_date.weekday())
        week_index = 0
        while len(results) < count:
            current_week = week_start + timedelta(weeks=week_index)
            for weekday in weekdays:
                d = current_week + timedelta(days=weekday)
                if d >= start_date:
                    results.append(d.isoformat())
                    if len(results) == count:
                        return results
            week_index += step
        return results

    if kind == "MONTHLY":
        step = int(parts[1])
        month_index = 0
        year, month = start_date.year, start_date.month

        while len(results) < count:
            total_month = (year * 12 + month - 1) + month_index
            y, m = divmod(total_month, 12)
            m += 1
            last_day = calendar.monthrange(y, m)[1]

            if len(parts) == 3:
                day_spec = int(parts[2])
                day = last_day if day_spec == -1 else day_spec
                if day <= last_day:
                    d = date(y, m, day)
                    if d >= start_date:
                        results.append(d.isoformat())
            else:
                n = int(parts[2])
                weekday = {
                    "MO": 0, "TU": 1, "WE": 2, "TH": 3,
                    "FR": 4, "SA": 5, "SU": 6
                }[parts[3]]

                if n == -1:
                    d = date(y, m, last_day)
                    d -= timedelta(days=(d.weekday() - weekday) % 7)
                else:
                    first = date(y, m, 1)
                    d = first + timedelta(days=(weekday - first.weekday()) % 7)
                    d += timedelta(weeks=n - 1)

                if d.month == m and d >= start_date:
                    results.append(d.isoformat())

            month_index += step
        return results

    if kind == "YEARLY":
        step = int(parts[1])
        target_month, target_day = map(int, parts[2].split("-"))
        year_index = 0

        while len(results) < count:
            y = start_date.year + year_index * step
            try:
                d = date(y, target_month, target_day)
            except ValueError:
                d = None

            if d is not None and d >= start_date:
                results.append(d.isoformat())

            year_index += 1

        return results

    raise ValueError("invalid recurrence rule")
