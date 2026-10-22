from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    begin = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    interval = int(parts[1])
    result = []

    def add_if_valid(y, m, d):
        try:
            candidate = date(y, m, d)
        except ValueError:
            return
        if candidate >= begin:
            result.append(candidate)

    if kind == "DAILY":
        for i in range(count):
            result.append(begin + timedelta(days=i * interval))

    elif kind == "WEEKLY":
        weekdays = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
        selected = {weekdays.index(code) for code in parts[2].split(",")}
        monday = begin - timedelta(days=begin.weekday())
        week = 0
        while len(result) < count:
            if week % interval == 0:
                for weekday in sorted(selected):
                    candidate = monday + timedelta(days=week * 7 + weekday)
                    if candidate >= begin:
                        result.append(candidate)
                        if len(result) == count:
                            break
            week += 1

    elif kind == "MONTHLY":
        start_month = begin.year * 12 + begin.month - 1
        if len(parts) == 3:
            day_spec = int(parts[2])
            month_index = start_month
            while len(result) < count:
                if (month_index - start_month) % interval == 0:
                    y, m0 = divmod(month_index, 12)
                    m = m0 + 1
                    last_day = calendar.monthrange(y, m)[1]
                    d = last_day if day_spec == -1 else day_spec
                    if d <= last_day:
                        add_if_valid(y, m, d)
                month_index += 1
        else:
            n = int(parts[2])
            weekday = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"].index(parts[3])
            month_index = start_month
            while len(result) < count:
                if (month_index - start_month) % interval == 0:
                    y, m0 = divmod(month_index, 12)
                    m = m0 + 1
                    first_weekday, last_day = calendar.monthrange(y, m)
                    if n == -1:
                        d = last_day - ((date(y, m, last_day).weekday() - weekday) % 7)
                    else:
                        d = 1 + ((weekday - first_weekday) % 7) + (n - 1) * 7
                    if d <= last_day:
                        add_if_valid(y, m, d)
                month_index += 1

    elif kind == "YEARLY":
        month, day = map(int, parts[2].split("-"))
        year = begin.year
        while len(result) < count:
            if (year - begin.year) % interval == 0:
                add_if_valid(year, month, day)
            year += 1

    return [d.isoformat() for d in result]
