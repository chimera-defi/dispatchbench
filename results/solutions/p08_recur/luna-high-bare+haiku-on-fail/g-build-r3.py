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

    elif kind == "WEEKLY":
        step = int(parts[1])
        weekdays = sorted(
            {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}[d]
            for d in parts[2].split(",")
        )
        week_start = start_date - timedelta(days=start_date.weekday())
        week_index = 0

        while len(result) < count:
            active_week = week_start + timedelta(weeks=week_index)
            for weekday in weekdays:
                current = active_week + timedelta(days=weekday)
                if current >= start_date:
                    result.append(current.isoformat())
                    if len(result) == count:
                        break
            week_index += step

    elif kind == "MONTHLY":
        step = int(parts[1])
        month_index = 0

        while len(result) < count:
            year, month0 = divmod(start_date.year * 12 + start_date.month - 1 + month_index, 12)
            month = month0 + 1
            _, last_day = calendar.monthrange(year, month)

            if len(parts) == 3:
                day = int(parts[2])
                day = last_day if day == -1 else day
                candidate = date(year, month, day) if day <= last_day else None
            else:
                occurrence = int(parts[2])
                weekday = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}[parts[3]]
                if occurrence == -1:
                    candidate_day = last_day - ((date(year, month, last_day).weekday() - weekday) % 7)
                else:
                    first_weekday = date(year, month, 1).weekday()
                    candidate_day = 1 + ((weekday - first_weekday) % 7) + 7 * (occurrence - 1)
                candidate = date(year, month, candidate_day) if candidate_day <= last_day else None

            if candidate is not None and candidate >= start_date:
                result.append(candidate.isoformat())
            month_index += step

    elif kind == "YEARLY":
        step = int(parts[1])
        month, day = map(int, parts[2].split("-"))
        year_offset = 0

        while len(result) < count:
            year = start_date.year + year_offset
            try:
                candidate = date(year, month, day)
            except ValueError:
                candidate = None
            if candidate is not None and candidate >= start_date:
                result.append(candidate.isoformat())
            year_offset += step

    return result
