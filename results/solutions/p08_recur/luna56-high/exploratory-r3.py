from datetime import date, timedelta


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    result = []

    def add_if_valid(candidate):
        if candidate >= start_date:
            result.append(candidate.strftime("%Y-%m-%d"))

    if parts[0] == "DAILY":
        step = int(parts[1])
        for i in range(count):
            add_if_valid(start_date + timedelta(days=i * step))
        return result

    if parts[0] == "WEEKLY":
        step = int(parts[1])
        weekdays = sorted(
            {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
             "FR": 4, "SA": 5, "SU": 6}[x]
            for x in parts[2].split(",")
        )
        base_monday = start_date - timedelta(days=start_date.weekday())
        week = 0
        while len(result) < count:
            monday = base_monday + timedelta(weeks=week)
            for weekday in weekdays:
                candidate = monday + timedelta(days=weekday)
                add_if_valid(candidate)
                if len(result) == count:
                    break
            week += step
        return result

    if parts[0] == "MONTHLY":
        step = int(parts[1])
        base_month = start_date.year * 12 + start_date.month - 1
        month_index = 0

        if len(parts) == 3:
            day_spec = int(parts[2])
            while len(result) < count:
                absolute_month = base_month + month_index
                year, month_zero = divmod(absolute_month, 12)
                month = month_zero + 1

                if day_spec == -1:
                    if month == 12:
                        next_month = date(year + 1, 1, 1)
                    else:
                        next_month = date(year, month + 1, 1)
                    candidate = next_month - timedelta(days=1)
                else:
                    try:
                        candidate = date(year, month, day_spec)
                    except ValueError:
                        candidate = None

                if candidate is not None:
                    add_if_valid(candidate)
                month_index += step
            return result

        n = int(parts[2])
        target_weekday = {
            "MO": 0, "TU": 1, "WE": 2, "TH": 3,
            "FR": 4, "SA": 5, "SU": 6
        }[parts[3]]

        while len(result) < count:
            absolute_month = base_month + month_index
            year, month_zero = divmod(absolute_month, 12)
            month = month_zero + 1

            if month == 12:
                next_month = date(year + 1, 1, 1)
            else:
                next_month = date(year, month + 1, 1)
            last_day = next_month - timedelta(days=1)

            if n == -1:
                offset = (last_day.weekday() - target_weekday) % 7
                candidate = last_day - timedelta(days=offset)
            else:
                first_day = date(year, month, 1)
                offset = (target_weekday - first_day.weekday()) % 7
                day = 1 + offset + 7 * (n - 1)
                candidate = (
                    date(year, month, day)
                    if day <= last_day.day else None
                )

            if candidate is not None:
                add_if_valid(candidate)
            month_index += step

        return result

    if parts[0] == "YEARLY":
        step = int(parts[1])
        month, day = map(int, parts[2].split("-"))
        year_offset = 0

        while len(result) < count:
            year = start_date.year + year_offset
            try:
                candidate = date(year, month, day)
            except ValueError:
                candidate = None

            if candidate is not None:
                add_if_valid(candidate)
            year_offset += step

        return result

    return result
