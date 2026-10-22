from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    interval = int(parts[1])
    results = []

    def add_if_valid(y, m, d):
        try:
            candidate = date(y, m, d)
        except ValueError:
            return
        if candidate >= start_date:
            results.append(candidate)

    if kind == "DAILY":
        current = start_date
        while len(results) < count:
            results.append(current)
            current += timedelta(days=interval)

    elif kind == "WEEKLY":
        weekdays = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                    "FR": 4, "SA": 5, "SU": 6}
        selected = sorted(weekdays[d] for d in parts[2].split(","))
        week_start = start_date - timedelta(days=start_date.weekday())
        week_index = 0
        while len(results) < count:
            if week_index % interval == 0:
                base = week_start + timedelta(weeks=week_index)
                for wd in selected:
                    candidate = base + timedelta(days=wd)
                    if candidate >= start_date:
                        results.append(candidate)
                        if len(results) == count:
                            break
            week_index += 1

    elif kind == "MONTHLY":
        if len(parts) == 3:
            day_spec = int(parts[2])
            month_index = 0
            while len(results) < count:
                year = start_date.year + (start_date.month - 1 + month_index) // 12
                month = (start_date.month - 1 + month_index) % 12 + 1
                last = calendar.monthrange(year, month)[1]
                day = last if day_spec == -1 else day_spec
                if day <= last:
                    add_if_valid(year, month, day)
                month_index += interval
        else:
            n = int(parts[2])
            wd = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                  "FR": 4, "SA": 5, "SU": 6}[parts[3]]
            month_index = 0
            while len(results) < count:
                year = start_date.year + (start_date.month - 1 + month_index) // 12
                month = (start_date.month - 1 + month_index) % 12 + 1
                first_wd, days_in_month = calendar.monthrange(year, month)
                if n == -1:
                    day = days_in_month - (calendar.weekday(year, month, days_in_month) - wd) % 7
                else:
                    day = 1 + (wd - first_wd) % 7 + 7 * (n - 1)
                if day <= days_in_month:
                    add_if_valid(year, month, day)
                month_index += interval

    elif kind == "YEARLY":
        month, day = map(int, parts[2].split("-"))
        year_offset = 0
        while len(results) < count:
            year = start_date.year + year_offset
            add_if_valid(year, month, day)
            year_offset += interval

    return [d.isoformat() for d in results]
