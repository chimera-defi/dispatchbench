from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    results = []

    def add(candidate):
        if candidate >= start_date:
            results.append(candidate.isoformat())

    if kind == "DAILY":
        step = int(parts[1])
        current = start_date
        while len(results) < count and current < date(3000, 1, 1):
            results.append(current.isoformat())
            current += timedelta(days=step)

    elif kind == "WEEKLY":
        step = int(parts[1])
        weekday_codes = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                         "FR": 4, "SA": 5, "SU": 6}
        weekdays = sorted(weekday_codes[code] for code in parts[2].split(","))
        monday = start_date - timedelta(days=start_date.weekday())
        week = 0
        while len(results) < count:
            week_start = monday + timedelta(weeks=week)
            if week_start >= date(3000, 1, 1):
                break
            for wd in weekdays:
                candidate = week_start + timedelta(days=wd)
                if candidate >= date(3000, 1, 1):
                    break
                add(candidate)
                if len(results) == count:
                    break
            week += step

    elif kind == "MONTHLY":
        step = int(parts[1])
        year0, month0 = start_date.year, start_date.month
        offset = 0

        if len(parts) == 3:
            day = int(parts[2])
            while len(results) < count:
                year, month = divmod((month0 - 1) + offset, 12)
                year += year0
                month += 1
                if year >= 3000:
                    break
                last_day = calendar.monthrange(year, month)[1]
                target_day = last_day if day == -1 else day
                if target_day <= last_day:
                    add(date(year, month, target_day))
                offset += step
        else:
            n = int(parts[2])
            wd = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                  "FR": 4, "SA": 5, "SU": 6}[parts[3]]
            while len(results) < count:
                year, month = divmod((month0 - 1) + offset, 12)
                year += year0
                month += 1
                if year >= 3000:
                    break
                last_day = calendar.monthrange(year, month)[1]
                if n == -1:
                    last = date(year, month, last_day)
                    target_day = last_day - (last.weekday() - wd) % 7
                else:
                    first = date(year, month, 1)
                    target_day = 1 + (wd - first.weekday()) % 7 + 7 * (n - 1)
                if target_day <= last_day:
                    add(date(year, month, target_day))
                offset += step

    elif kind == "YEARLY":
        step = int(parts[1])
        month, day = map(int, parts[2].split("-"))
        year = start_date.year
        while len(results) < count and year < 3000:
            try:
                add(date(year, month, day))
            except ValueError:
                pass
            year += step

    return results
