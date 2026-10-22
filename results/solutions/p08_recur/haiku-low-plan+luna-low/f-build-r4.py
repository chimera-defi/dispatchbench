from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    out = []

    if kind == "DAILY":
        step = int(parts[1])
        current = start_date
        for _ in range(count):
            out.append(current.isoformat())
            current += timedelta(days=step)
        return out

    if kind == "WEEKLY":
        interval = int(parts[1])
        weekdays = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                    "FR": 4, "SA": 5, "SU": 6}
        days = sorted(weekdays[code] for code in parts[2].split(","))
        week0 = start_date - timedelta(days=start_date.weekday())
        week_index = 0

        while len(out) < count:
            monday = week0 + timedelta(weeks=week_index)
            for weekday in days:
                candidate = monday + timedelta(days=weekday)
                if candidate >= start_date:
                    out.append(candidate.isoformat())
                    if len(out) == count:
                        break
            week_index += interval
        return out

    if kind == "MONTHLY":
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
            weekdays = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                        "FR": 4, "SA": 5, "SU": 6}
            weekday = weekdays[parts[3]]

            while len(out) < count:
                year, month0 = divmod(month_index, 12)
                month = month0 + 1
                last_day = calendar.monthrange(year, month)[1]

                if occurrence == -1:
                    last = date(year, month, last_day)
                    actual_day = last_day - (last.weekday() - weekday) % 7
                else:
                    first = date(year, month, 1)
                    actual_day = 1 + (weekday - first.weekday()) % 7
                    actual_day += 7 * (occurrence - 1)

                if actual_day <= last_day:
                    candidate = date(year, month, actual_day)
                    if candidate >= start_date:
                        out.append(candidate.isoformat())
                month_index += interval
        return out

    if kind == "YEARLY":
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
        return out

    raise ValueError("Unknown recurrence rule")
