from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    interval = int(parts[1])
    result = []

    def add_if_valid(candidate):
        if candidate is not None and candidate >= start_date:
            result.append(candidate)

    if kind == "DAILY":
        for i in range(count):
            result.append(start_date + timedelta(days=i * interval))

    elif kind == "WEEKLY":
        weekdays = set(parts[2].split(","))
        weekday_codes = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                         "FR": 4, "SA": 5, "SU": 6}
        offsets = sorted(weekday_codes[day] for day in weekdays)
        week_start = start_date - timedelta(days=start_date.weekday())
        week_index = 0
        while len(result) < count:
            if week_index % interval == 0:
                for offset in offsets:
                    candidate = week_start + timedelta(days=week_index * 7 + offset)
                    add_if_valid(candidate)
                    if len(result) == count:
                        break
            week_index += 1

    elif kind == "MONTHLY":
        if len(parts) == 3:
            day_spec = int(parts[2])
            month_index = 0
            while len(result) < count:
                total_month = (start_date.year - 1) * 12 + (start_date.month - 1) + month_index * interval
                year, month0 = divmod(total_month, 12)
                year += 1
                month = month0 + 1
                last_day = calendar.monthrange(year, month)[1]
                day = last_day if day_spec == -1 else day_spec
                if day <= last_day:
                    add_if_valid(date(year, month, day))
                month_index += 1
        else:
            nth = int(parts[2])
            weekday = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                       "FR": 4, "SA": 5, "SU": 6}[parts[3]]
            month_index = 0
            while len(result) < count:
                total_month = (start_date.year - 1) * 12 + (start_date.month - 1) + month_index * interval
                year, month0 = divmod(total_month, 12)
                year += 1
                month = month0 + 1
                cal = calendar.monthcalendar(year, month)
                matching_days = [week[weekday] for week in cal if week[weekday] != 0]
                if nth == -1:
                    day = matching_days[-1]
                elif nth <= len(matching_days):
                    day = matching_days[nth - 1]
                else:
                    day = None
                if day is not None:
                    add_if_valid(date(year, month, day))
                month_index += 1

    elif kind == "YEARLY":
        month, day = map(int, parts[2].split("-"))
        year_index = 0
        while len(result) < count:
            year = start_date.year + year_index * interval
            try:
                candidate = date(year, month, day)
            except ValueError:
                candidate = None
            add_if_valid(candidate)
            year_index += 1

    return [d.isoformat() for d in result]
