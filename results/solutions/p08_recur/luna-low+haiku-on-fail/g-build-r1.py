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
        current = start_date
        while len(results) < count:
            add(current)
            current += timedelta(days=interval)
        return results

    if kind == "WEEKLY":
        weekdays = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}
        selected = sorted(weekdays[code] for code in parts[2].split(","))
        monday = start_date - timedelta(days=start_date.weekday())
        week = 0
        while len(results) < count:
            week_start = monday + timedelta(weeks=week)
            for weekday in selected:
                add(week_start + timedelta(days=weekday))
                if len(results) == count:
                    break
            week += interval
        return results

    if kind == "MONTHLY":
        if len(parts) == 3:
            day_spec = int(parts[2])
            year, month = start_date.year, start_date.month
            month_index = 0
            while len(results) < count:
                current_year, current_month = year, month + month_index
                current_year += (current_month - 1) // 12
                current_month = (current_month - 1) % 12 + 1
                last_day = calendar.monthrange(current_year, current_month)[1]
                day = last_day if day_spec == -1 else day_spec
                if day <= last_day:
                    add(date(current_year, current_month, day))
                month_index += interval
        else:
            nth = int(parts[2])
            weekday = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}[parts[3]]
            year, month = start_date.year, start_date.month
            month_index = 0
            while len(results) < count:
                current_year, current_month = year, month + month_index
                current_year += (current_month - 1) // 12
                current_month = (current_month - 1) % 12 + 1
                first_weekday, days_in_month = calendar.monthrange(current_year, current_month)
                if nth == -1:
                    last_weekday = (first_weekday + days_in_month - 1) % 7
                    day = days_in_month - (last_weekday - weekday) % 7
                else:
                    day = 1 + (weekday - first_weekday) % 7 + 7 * (nth - 1)
                    if day > days_in_month:
                        day = None
                if day is not None:
                    add(date(current_year, current_month, day))
                month_index += interval
        return results

    if kind == "YEARLY":
        month, day = map(int, parts[2].split("-"))
        year = start_date.year
        year_index = 0
        while len(results) < count:
            candidate_year = year + year_index
            try:
                add(date(candidate_year, month, day))
            except ValueError:
                pass
            year_index += interval
        return results
