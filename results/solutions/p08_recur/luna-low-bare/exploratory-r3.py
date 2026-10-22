from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    interval = int(parts[1])
    results = []

    def add(candidate):
        if candidate >= start_date:
            results.append(candidate.isoformat())

    if kind == "DAILY":
        for i in range(count):
            add(start_date + timedelta(days=i * interval))
        return results

    if kind == "WEEKLY":
        weekdays = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                    "FR": 4, "SA": 5, "SU": 6}
        selected = sorted(weekdays[code] for code in parts[2].split(","))
        week_start = start_date - timedelta(days=start_date.weekday())
        week_index = 0
        while len(results) < count:
            base = week_start + timedelta(weeks=week_index * interval)
            for wd in selected:
                add(base + timedelta(days=wd))
                if len(results) == count:
                    break
            week_index += 1
        return results

    if kind == "MONTHLY":
        if len(parts) == 3:
            day_spec = int(parts[2])
            month_index = 0
            while len(results) < count:
                year = start_date.year + (start_date.month - 1 + month_index * interval) // 12
                month = (start_date.month - 1 + month_index * interval) % 12 + 1
                last_day = calendar.monthrange(year, month)[1]
                day = last_day if day_spec == -1 else day_spec
                if day <= last_day:
                    add(date(year, month, day))
                month_index += 1
        else:
            nth = int(parts[2])
            weekday = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                       "FR": 4, "SA": 5, "SU": 6}[parts[3]]
            month_index = 0
            while len(results) < count:
                year = start_date.year + (start_date.month - 1 + month_index * interval) // 12
                month = (start_date.month - 1 + month_index * interval) % 12 + 1
                month_days = calendar.monthrange(year, month)[1]
                if nth == -1:
                    last = date(year, month, month_days)
                    day = month_days - (last.weekday() - weekday) % 7
                else:
                    first = date(year, month, 1)
                    day = 1 + (weekday - first.weekday()) % 7 + (nth - 1) * 7
                if day <= month_days:
                    add(date(year, month, day))
                month_index += 1
        return results

    if kind == "YEARLY":
        month, day = map(int, parts[2].split("-"))
        year_index = 0
        while len(results) < count:
            year = start_date.year + year_index * interval
            try:
                add(date(year, month, day))
            except ValueError:
                pass
            year_index += 1
        return results

    return results
