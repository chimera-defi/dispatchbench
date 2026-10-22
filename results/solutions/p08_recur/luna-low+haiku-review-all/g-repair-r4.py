from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    begin = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    step = int(parts[1])
    results = []

    def add_if_valid(candidate):
        if candidate is not None and candidate >= begin:
            results.append(candidate)

    if kind == "DAILY":
        current = begin
        while len(results) < count:
            results.append(current)
            current += timedelta(days=step)

    elif kind == "WEEKLY":
        weekdays = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                    "FR": 4, "SA": 5, "SU": 6}
        selected = sorted(weekdays[code] for code in parts[2].split(","))
        week_start = begin - timedelta(days=begin.weekday())
        week_index = 0

        while len(results) < count:
            if week_index % step == 0:
                for weekday in selected:
                    candidate = week_start + timedelta(days=weekday)
                    add_if_valid(candidate)
                    if len(results) == count:
                        break
            week_index += 1
            week_start += timedelta(days=7)

    elif kind == "MONTHLY":
        start_month = begin.year * 12 + begin.month - 1
        month_index = 0

        while len(results) < count:
            if month_index % step == 0:
                year, month0 = divmod(start_month + month_index, 12)
                month = month0 + 1
                last_day = calendar.monthrange(year, month)[1]

                if len(parts) == 3:
                    day = last_day if parts[2] == "-1" else int(parts[2])
                    candidate = date(year, month, day) if day <= last_day else None
                else:
                    ordinal = int(parts[2])
                    weekday = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                               "FR": 4, "SA": 5, "SU": 6}[parts[3]]
                    first_weekday, days_in_month = calendar.monthrange(year, month)
                    if ordinal == -1:
                        day = days_in_month - ((first_weekday + days_in_month - 1 - weekday) % 7)
                    else:
                        day = 1 + ((weekday - first_weekday) % 7) + 7 * (ordinal - 1)
                        if day > days_in_month:
                            day = None
                    candidate = date(year, month, day) if day is not None else None

                add_if_valid(candidate)
            month_index += 1

    elif kind == "YEARLY":
        month, day = map(int, parts[2].split("-"))
        year_index = 0
        while len(results) < count:
            year = begin.year + year_index
            if year_index % step == 0:
                try:
                    candidate = date(year, month, day)
                except ValueError:
                    candidate = None
                add_if_valid(candidate)
            year_index += 1

    return [d.isoformat() for d in results]
