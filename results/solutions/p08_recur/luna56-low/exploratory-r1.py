from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    result = []

    def fmt(d):
        return d.isoformat()

    if parts[0] == "DAILY":
        step = int(parts[1])
        d = start_date
        for _ in range(count):
            result.append(fmt(d))
            d += timedelta(days=step)
        return result

    if parts[0] == "WEEKLY":
        step = int(parts[1])
        weekdays = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
        wanted = {weekdays.index(x) for x in parts[2].split(",")}
        week_start = start_date - timedelta(days=start_date.weekday())
        week_index = 0
        while len(result) < count:
            current_week = week_start + timedelta(weeks=week_index * step)
            for wd in sorted(wanted):
                d = current_week + timedelta(days=wd)
                if d >= start_date:
                    result.append(fmt(d))
                    if len(result) == count:
                        return result
            week_index += 1
        return result

    if parts[0] == "MONTHLY":
        step = int(parts[1])
        month_start_index = start_date.year * 12 + start_date.month - 1
        index = 0

        while len(result) < count:
            absolute = month_start_index + index * step
            year, month_zero = divmod(absolute, 12)
            month = month_zero + 1
            last_day = calendar.monthrange(year, month)[1]

            if len(parts) == 3:
                day_spec = int(parts[2])
                day = last_day if day_spec == -1 else day_spec
                if day <= last_day:
                    d = date(year, month, day)
                    if d >= start_date:
                        result.append(fmt(d))
            else:
                n = int(parts[2])
                wd = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"].index(parts[3])
                first = date(year, month, 1)
                if n == -1:
                    d = date(year, month, last_day)
                    d -= timedelta(days=(d.weekday() - wd) % 7)
                else:
                    d = first + timedelta(days=(wd - first.weekday()) % 7)
                    d += timedelta(weeks=n - 1)
                    if d.month != month:
                        d = None
                if d is not None and d >= start_date:
                    result.append(fmt(d))

            index += 1
        return result

    if parts[0] == "YEARLY":
        step = int(parts[1])
        month, day = map(int, parts[2].split("-"))
        year = start_date.year
        offset = 0

        while len(result) < count:
            y = year + offset * step
            try:
                d = date(y, month, day)
                if d >= start_date:
                    result.append(fmt(d))
            except ValueError:
                pass
            offset += 1

        return result
