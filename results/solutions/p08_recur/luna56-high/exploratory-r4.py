from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    results = []

    def add(d):
        if d >= start_date:
            results.append(d.isoformat())

    if parts[0] == "DAILY":
        step = int(parts[1])
        for i in range(count):
            results.append((start_date + timedelta(days=i * step)).isoformat())
        return results

    if parts[0] == "WEEKLY":
        step = int(parts[1])
        weekdays = sorted("MO TU WE TH FR SA SU".split().index(x)
                          for x in parts[2].split(","))
        week_start = start_date - timedelta(days=start_date.weekday())
        week_index = 0

        while len(results) < count:
            base = week_start + timedelta(days=week_index * step * 7)
            for weekday in weekdays:
                add(base + timedelta(days=weekday))
                if len(results) == count:
                    return results
            week_index += 1
        return results

    if parts[0] == "MONTHLY":
        step = int(parts[1])
        base_month = start_date.year * 12 + start_date.month - 1
        month_index = 0

        while len(results) < count:
            absolute_month = base_month + month_index * step
            year, month_zero = divmod(absolute_month, 12)
            month = month_zero + 1
            last_day = calendar.monthrange(year, month)[1]

            if len(parts) == 3:
                day_spec = int(parts[2])
                day = last_day if day_spec == -1 else day_spec
                if day <= last_day:
                    add(date(year, month, day))
            else:
                n = int(parts[2])
                weekday = "MO TU WE TH FR SA SU".split().index(parts[3])
                if n == -1:
                    day = last_day
                    while date(year, month, day).weekday() != weekday:
                        day -= 1
                    add(date(year, month, day))
                else:
                    first_weekday = date(year, month, 1).weekday()
                    day = 1 + (weekday - first_weekday) % 7 + (n - 1) * 7
                    if day <= last_day:
                        add(date(year, month, day))

            month_index += 1
        return results

    if parts[0] == "YEARLY":
        step = int(parts[1])
        month, day = map(int, parts[2].split("-"))
        year_index = 0

        while len(results) < count:
            year = start_date.year + year_index * step
            try:
                add(date(year, month, day))
            except ValueError:
                pass
            year_index += 1

        return results

    return results
