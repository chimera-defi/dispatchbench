from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    result = []

    def add_if_valid(d):
        if d >= start_date:
            result.append(d.isoformat())

    kind = parts[0]

    if kind == "DAILY":
        k = int(parts[1])
        current = start_date
        for _ in range(count):
            result.append(current.isoformat())
            current += timedelta(days=k)
        return result

    if kind == "WEEKLY":
        k = int(parts[1])
        weekdays = sorted(
            {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
             "FR": 4, "SA": 5, "SU": 6}[x]
            for x in parts[2].split(",")
        )
        week_start = start_date - timedelta(days=start_date.weekday())
        week_index = 0

        while len(result) < count:
            current_week = week_start + timedelta(weeks=week_index * k)
            for wd in weekdays:
                add_if_valid(current_week + timedelta(days=wd))
                if len(result) == count:
                    return result
            week_index += 1

        return result

    if kind == "MONTHLY":
        k = int(parts[1])
        month_index = 0
        year, month = start_date.year, start_date.month

        if len(parts) == 3:
            day_spec = int(parts[2])

            while len(result) < count:
                total_month = (year * 12 + (month - 1)) + month_index * k
                y, m0 = divmod(total_month, 12)
                m = m0 + 1
                last_day = calendar.monthrange(y, m)[1]
                day = last_day if day_spec == -1 else day_spec

                if day <= last_day:
                    add_if_valid(date(y, m, day))
                month_index += 1

        else:
            n = int(parts[2])
            wd = {
                "MO": 0, "TU": 1, "WE": 2, "TH": 3,
                "FR": 4, "SA": 5, "SU": 6
            }[parts[3]]

            while len(result) < count:
                total_month = (year * 12 + (month - 1)) + month_index * k
                y, m0 = divmod(total_month, 12)
                m = m0 + 1
                first_wd = date(y, m, 1).weekday()
                days_in_month = calendar.monthrange(y, m)[1]

                if n == -1:
                    last = date(y, m, days_in_month)
                    offset = (last.weekday() - wd) % 7
                    day = days_in_month - offset
                else:
                    day = 1 + (wd - first_wd) % 7 + (n - 1) * 7

                if day <= days_in_month:
                    add_if_valid(date(y, m, day))
                month_index += 1

        return result

    if kind == "YEARLY":
        k = int(parts[1])
        target_month, target_day = map(int, parts[2].split("-"))
        year_index = 0

        while len(result) < count:
            y = start_date.year + year_index * k
            try:
                add_if_valid(date(y, target_month, target_day))
            except ValueError:
                pass
            year_index += 1

        return result

    return result
