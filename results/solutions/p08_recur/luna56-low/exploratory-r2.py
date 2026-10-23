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
            base = week_start + timedelta(days=week_index * step * 7)
            for weekday in weekdays:
                candidate = base + timedelta(days=weekday)
                if candidate >= start_date:
                    result.append(candidate.isoformat())
                    if len(result) == count:
                        return result
            week_index += 1

        return result

    if kind == "MONTHLY":
        step = int(parts[1])
        start_month_index = start_date.year * 12 + start_date.month - 1
        month_index = 0

        if len(parts) == 3:
            day_spec = int(parts[2])

            while len(result) < count:
                absolute_month = start_month_index + month_index * step
                year, month_zero = divmod(absolute_month, 12)
                month = month_zero + 1
                last_day = calendar.monthrange(year, month)[1]

                day = last_day if day_spec == -1 else day_spec
                if day <= last_day:
                    candidate = date(year, month, day)
                    if candidate >= start_date:
                        result.append(candidate.isoformat())

                month_index += 1

            return result

        ordinal = int(parts[2])
        weekday = {
            "MO": 0, "TU": 1, "WE": 2, "TH": 3,
            "FR": 4, "SA": 5, "SU": 6
        }[parts[3]]

        while len(result) < count:
            absolute_month = start_month_index + month_index * step
            year, month_zero = divmod(absolute_month, 12)
            month = month_zero + 1
            last_day = calendar.monthrange(year, month)[1]

            if ordinal == -1:
                last = date(year, month, last_day)
                offset = (last.weekday() - weekday) % 7
                candidate = last - timedelta(days=offset)
            else:
                first = date(year, month, 1)
                offset = (weekday - first.weekday()) % 7
                day = 1 + offset + (ordinal - 1) * 7
                candidate = date(year, month, day) if day <= last_day else None

            if candidate is not None and candidate >= start_date:
                result.append(candidate.isoformat())

            month_index += 1

        return result

    if kind == "YEARLY":
        step = int(parts[1])
        target_month, target_day = map(int, parts[2].split("-"))
        year_index = 0
        start_year = start_date.year

        while len(result) < count:
            year = start_year + year_index * step
            if target_day <= calendar.monthrange(year, target_month)[1]:
                candidate = date(year, target_month, target_day)
                if candidate >= start_date:
                    result.append(candidate.isoformat())
            year_index += 1

        return result

    raise ValueError("Invalid recurrence rule")
