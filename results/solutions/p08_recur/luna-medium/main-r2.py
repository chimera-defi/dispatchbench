from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    interval = int(parts[1])
    results = []

    def add(candidate):
        if candidate is not None and candidate >= start_date:
            results.append(candidate.isoformat())

    if kind == "DAILY":
        for i in range(count):
            add(start_date + timedelta(days=i * interval))

    elif kind == "WEEKLY":
        weekdays = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                    "FR": 4, "SA": 5, "SU": 6}
        selected = sorted(weekdays[code] for code in parts[2].split(","))
        week_start = start_date - timedelta(days=start_date.weekday())
        week_index = 0

        while len(results) < count:
            base = week_start + timedelta(weeks=week_index * interval)
            for weekday in selected:
                candidate = base + timedelta(days=weekday)
                add(candidate)
                if len(results) == count:
                    break
            week_index += 1

    elif kind == "MONTHLY":
        if len(parts) == 3:
            day = int(parts[2])
            month_index = 0

            while len(results) < count:
                year = start_date.year + (start_date.month - 1 + month_index * interval) // 12
                month = (start_date.month - 1 + month_index * interval) % 12 + 1
                last_day = calendar.monthrange(year, month)[1]
                target_day = last_day if day == -1 else day
                if target_day <= last_day:
                    add(date(year, month, target_day))
                month_index += 1
        else:
            occurrence = int(parts[2])
            weekday = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                       "FR": 4, "SA": 5, "SU": 6}[parts[3]]
            month_index = 0

            while len(results) < count:
                year = start_date.year + (start_date.month - 1 + month_index * interval) // 12
                month = (start_date.month - 1 + month_index * interval) % 12 + 1
                first_weekday, days_in_month = calendar.monthrange(year, month)

                if occurrence == -1:
                    last_weekday = (first_weekday + days_in_month - 1) % 7
                    day = days_in_month - ((last_weekday - weekday) % 7)
                else:
                    day = 1 + ((weekday - first_weekday) % 7) + 7 * (occurrence - 1)

                if day <= days_in_month:
                    add(date(year, month, day))
                month_index += 1

    elif kind == "YEARLY":
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
