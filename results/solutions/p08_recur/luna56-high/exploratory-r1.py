from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    weekdays = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                "FR": 4, "SA": 5, "SU": 6}

    result = []

    if kind == "DAILY":
        step = int(parts[1])
        for i in range(count):
            result.append((start_date + timedelta(days=i * step)).isoformat())
        return result

    if kind == "WEEKLY":
        step = int(parts[1])
        wanted = sorted(weekdays[x] for x in parts[2].split(","))
        week_start = start_date - timedelta(days=start_date.weekday())
        week_index = 0

        while len(result) < count:
            current_week = week_start + timedelta(weeks=week_index)
            for wd in wanted:
                candidate = current_week + timedelta(days=wd)
                if candidate >= start_date:
                    result.append(candidate.isoformat())
                    if len(result) == count:
                        return result
            week_index += step

        return result

    if kind == "MONTHLY":
        step = int(parts[1])
        month_index = 0

        while len(result) < count:
            absolute_month = start_date.year * 12 + start_date.month - 1
            current_month = absolute_month + month_index * step
            year, month_zero = divmod(current_month, 12)
            month = month_zero + 1
            last_day = calendar.monthrange(year, month)[1]

            if len(parts) == 3:
                day_spec = int(parts[2])
                day = last_day if day_spec == -1 else day_spec
                if day <= last_day:
                    candidate = date(year, month, day)
                    if candidate >= start_date:
                        result.append(candidate.isoformat())
            else:
                n = int(parts[2])
                target_weekday = weekdays[parts[3]]

                if n == -1:
                    candidate = date(year, month, last_day)
                    candidate -= timedelta(
                        days=(candidate.weekday() - target_weekday) % 7
                    )
                else:
                    first = date(year, month, 1)
                    candidate = first + timedelta(
                        days=(target_weekday - first.weekday()) % 7 + 7 * (n - 1)
                    )

                if candidate.month == month and candidate >= start_date:
                    result.append(candidate.isoformat())

            month_index += 1

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

    return result
