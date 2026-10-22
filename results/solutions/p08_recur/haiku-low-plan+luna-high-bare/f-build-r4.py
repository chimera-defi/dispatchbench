from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    weekdays = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}

    if kind == "DAILY":
        interval = int(parts[1])
        return [
            (start_date + timedelta(days=interval * i)).isoformat()
            for i in range(count)
        ]

    out = []

    if kind == "WEEKLY":
        interval = int(parts[1])
        days = sorted({weekdays[code] for code in parts[2].split(",")})
        monday = start_date - timedelta(days=start_date.weekday())
        week = 0
        while len(out) < count:
            week_start = monday + timedelta(weeks=week)
            for day in days:
                candidate = week_start + timedelta(days=day)
                if candidate >= start_date:
                    out.append(candidate.isoformat())
                    if len(out) == count:
                        break
            week += interval

    elif kind == "MONTHLY":
        interval = int(parts[1])
        month_index = start_date.year * 12 + start_date.month - 1

        if len(parts) == 3:
            day = int(parts[2])
            while len(out) < count:
                year, month0 = divmod(month_index, 12)
                month = month0 + 1
                last_day = calendar.monthrange(year, month)[1]
                actual_day = last_day if day == -1 else day
                if actual_day <= last_day:
                    candidate = date(year, month, actual_day)
                    if candidate >= start_date:
                        out.append(candidate.isoformat())
                month_index += interval
        else:
            occurrence = int(parts[2])
            weekday = weekdays[parts[3]]
            while len(out) < count:
                year, month0 = divmod(month_index, 12)
                month = month0 + 1
                last_day = calendar.monthrange(year, month)[1]

                if occurrence == -1:
                    last = date(year, month, last_day)
                    day = last_day - (last.weekday() - weekday) % 7
                else:
                    first = date(year, month, 1)
                    day = 1 + (weekday - first.weekday()) % 7 + 7 * (occurrence - 1)

                if day <= last_day:
                    candidate = date(year, month, day)
                    if candidate >= start_date:
                        out.append(candidate.isoformat())
                month_index += interval

    elif kind == "YEARLY":
        interval = int(parts[1])
        month, day = map(int, parts[2].split("-"))
        year = start_date.year
        while len(out) < count:
            try:
                candidate = date(year, month, day)
                if candidate >= start_date:
                    out.append(candidate.isoformat())
            except ValueError:
                pass
            year += interval

    else:
        raise ValueError("Unknown recurrence rule")

    return out
