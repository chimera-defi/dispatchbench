from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    parts = rule.split()
    kind = parts[0]
    k = int(parts[1])
    first = date.fromisoformat(start)
    result = []

    def add_if_valid(year, month, day):
        try:
            candidate = date(year, month, day)
        except ValueError:
            return
        if candidate >= first:
            result.append(candidate)

    if kind == "DAILY":
        current = first
        step = timedelta(days=k)
        for _ in range(count):
            result.append(current)
            current += step

    elif kind == "WEEKLY":
        weekday_codes = {
            "MO": 0, "TU": 1, "WE": 2, "TH": 3,
            "FR": 4, "SA": 5, "SU": 6,
        }
        weekdays = sorted(weekday_codes[code] for code in parts[2].split(","))
        week_start = first - timedelta(days=first.weekday())
        week_index = 0
        while len(result) < count:
            if week_index % k == 0:
                for weekday in weekdays:
                    candidate = week_start + timedelta(days=week_index * 7 + weekday)
                    if candidate >= first:
                        result.append(candidate)
                        if len(result) == count:
                            break
            week_index += 1

    elif kind == "MONTHLY":
        if len(parts) == 3:
            day_spec = int(parts[2])
            month_index = 0
            while len(result) < count:
                if month_index % k == 0:
                    year = first.year + (first.month - 1 + month_index) // 12
                    month = (first.month - 1 + month_index) % 12 + 1
                    last_day = calendar.monthrange(year, month)[1]
                    day = last_day if day_spec == -1 else day_spec
                    if day <= last_day:
                        add_if_valid(year, month, day)
                month_index += 1
        else:
            n = int(parts[2])
            weekday = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                       "FR": 4, "SA": 5, "SU": 6}[parts[3]]
            month_index = 0
            while len(result) < count:
                if month_index % k == 0:
                    year = first.year + (first.month - 1 + month_index) // 12
                    month = (first.month - 1 + month_index) % 12 + 1
                    last_day = calendar.monthrange(year, month)[1]
                    if n == -1:
                        last_date = date(year, month, last_day)
                        offset = (last_date.weekday() - weekday) % 7
                        day = last_day - offset
                    else:
                        first_day = date(year, month, 1)
                        offset = (weekday - first_day.weekday()) % 7
                        day = 1 + offset + 7 * (n - 1)
                    if day <= last_day:
                        add_if_valid(year, month, day)
                month_index += 1

    elif kind == "YEARLY":
        month, day = map(int, parts[2].split("-"))
        year_index = 0
        while len(result) < count:
            if year_index % k == 0:
                add_if_valid(first.year + year_index, month, day)
            year_index += 1

    return [d.isoformat() for d in result[:count]]
