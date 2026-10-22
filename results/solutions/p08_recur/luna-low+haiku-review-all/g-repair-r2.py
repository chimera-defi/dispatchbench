from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    interval = int(parts[1])
    results = []

    def add_if_valid(candidate):
        if candidate is not None and candidate >= start_date:
            results.append(candidate.isoformat())

    if kind == "DAILY":
        current = start_date
        for _ in range(count):
            results.append(current.isoformat())
            current += timedelta(days=interval)
        return results

    if kind == "WEEKLY":
        weekdays = {
            "MO": 0, "TU": 1, "WE": 2, "TH": 3,
            "FR": 4, "SA": 5, "SU": 6,
        }
        selected = sorted(weekdays[day] for day in parts[2].split(","))
        week_start = start_date - timedelta(days=start_date.weekday())
        week_index = 0
        while len(results) < count:
            active_start = week_start + timedelta(weeks=week_index * interval)
            for weekday in selected:
                candidate = active_start + timedelta(days=weekday)
                add_if_valid(candidate)
                if len(results) == count:
                    return results
            week_index += 1
        return results

    if kind == "MONTHLY":
        start_month = start_date.year * 12 + start_date.month - 1
        if len(parts) == 3:
            day_spec = int(parts[2])
            for step in range(10000):
                month_index = start_month + step * interval
                year, month0 = divmod(month_index, 12)
                month = month0 + 1
                last_day = calendar.monthrange(year, month)[1]
                day = last_day if day_spec == -1 else day_spec
                if day <= last_day:
                    add_if_valid(date(year, month, day))
                    if len(results) == count:
                        return results
        else:
            nth = int(parts[2])
            weekday = {
                "MO": 0, "TU": 1, "WE": 2, "TH": 3,
                "FR": 4, "SA": 5, "SU": 6,
            }[parts[3]]
            for step in range(10000):
                month_index = start_month + step * interval
                year, month0 = divmod(month_index, 12)
                month = month0 + 1
                first_weekday, days_in_month = calendar.monthrange(year, month)
                if nth == -1:
                    last_weekday = (first_weekday + days_in_month - 1) % 7
                    day = days_in_month - (last_weekday - weekday) % 7
                else:
                    day = 1 + (weekday - first_weekday) % 7 + (nth - 1) * 7
                    if day > days_in_month:
                        continue
                add_if_valid(date(year, month, day))
                if len(results) == count:
                    return results
        return results

    if kind == "YEARLY":
        month, day = map(int, parts[2].split("-"))
        for step in range(10000):
            year = start_date.year + step * interval
            if year > 9999:
                break
            try:
                candidate = date(year, month, day)
            except ValueError:
                continue
            add_if_valid(candidate)
            if len(results) == count:
                return results
        return results

    return results
