from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    result = []

    def add(candidate):
        if candidate >= start_date:
            result.append(candidate.isoformat())

    if kind == "DAILY":
        step = int(parts[1])
        current = start_date
        while len(result) < count:
            add(current)
            current += timedelta(days=step)

    elif kind == "WEEKLY":
        step = int(parts[1])
        weekday_index = {
            "MO": 0, "TU": 1, "WE": 2, "TH": 3,
            "FR": 4, "SA": 5, "SU": 6,
        }
        weekdays = sorted(weekday_index[code] for code in parts[2].split(","))
        week_start = start_date - timedelta(days=start_date.weekday())
        week_offset = 0
        while len(result) < count:
            active_week = week_start + timedelta(weeks=week_offset)
            for weekday in weekdays:
                add(active_week + timedelta(days=weekday))
                if len(result) == count:
                    break
            week_offset += step

    elif kind == "MONTHLY":
        step = int(parts[1])
        month_index = start_date.year * 12 + start_date.month - 1
        month_offset = 0

        while len(result) < count:
            index = month_index + month_offset
            year, month0 = divmod(index, 12)
            month = month0 + 1
            last_day = calendar.monthrange(year, month)[1]

            if len(parts) == 3:
                day_spec = int(parts[2])
                day = last_day if day_spec == -1 else day_spec
                if day <= last_day:
                    add(date(year, month, day))
            else:
                occurrence = int(parts[2])
                target_weekday = {
                    "MO": 0, "TU": 1, "WE": 2, "TH": 3,
                    "FR": 4, "SA": 5, "SU": 6,
                }[parts[3]]

                if occurrence == -1:
                    last_date = date(year, month, last_day)
                    day = last_day - (last_date.weekday() - target_weekday) % 7
                    add(date(year, month, day))
                else:
                    first_date = date(year, month, 1)
                    first_match_day = 1 + (target_weekday - first_date.weekday()) % 7
                    day = first_match_day + 7 * (occurrence - 1)
                    if day <= last_day:
                        add(date(year, month, day))

            month_offset += step

    elif kind == "YEARLY":
        step = int(parts[1])
        month, day = map(int, parts[2].split("-"))
        year = start_date.year
        while len(result) < count and year < 3000:
            try:
                add(date(year, month, day))
            except ValueError:
                pass
            year += step

    return result
