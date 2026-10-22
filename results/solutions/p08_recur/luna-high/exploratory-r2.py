from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    result = []

    def add(d: date) -> None:
        result.append(f"{d.year:04d}-{d.month:02d}-{d.day:02d}")

    if kind == "DAILY":
        step = int(parts[1])
        for i in range(count):
            add(start_date + timedelta(days=i * step))

    elif kind == "WEEKLY":
        step = int(parts[1])
        weekday_numbers = {
            "MO": 0, "TU": 1, "WE": 2, "TH": 3,
            "FR": 4, "SA": 5, "SU": 6,
        }
        weekdays = sorted(weekday_numbers[day] for day in parts[2].split(","))
        first_monday = start_date - timedelta(days=start_date.weekday())
        week_index = 0

        while len(result) < count:
            monday = first_monday + timedelta(weeks=week_index * step)
            for weekday in weekdays:
                candidate = monday + timedelta(days=weekday)
                if candidate >= start_date:
                    add(candidate)
                    if len(result) == count:
                        break
            week_index += 1

    elif kind == "MONTHLY":
        step = int(parts[1])
        month_index = 0

        while len(result) < count:
            year, month = divmod(start_date.year * 12 + start_date.month - 1 + month_index * step, 12)
            month += 1
            last_day = calendar.monthrange(year, month)[1]

            if len(parts) == 3:
                day = int(parts[2])
                if day == -1:
                    day = last_day
                if 1 <= day <= last_day:
                    candidate = date(year, month, day)
                    if candidate >= start_date:
                        add(candidate)
            else:
                occurrence = int(parts[2])
                weekday = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                           "FR": 4, "SA": 5, "SU": 6}[parts[3]]
                if occurrence == -1:
                    day = last_day - (date(year, month, last_day).weekday() - weekday) % 7
                else:
                    day = 1 + (weekday - date(year, month, 1).weekday()) % 7 + (occurrence - 1) * 7
                if day <= last_day:
                    candidate = date(year, month, day)
                    if candidate >= start_date:
                        add(candidate)

            month_index += 1

    else:  # YEARLY
        step = int(parts[1])
        month, day = map(int, parts[2].split("-"))
        year_index = 0

        while len(result) < count:
            year = start_date.year + year_index * step
            try:
                candidate = date(year, month, day)
                if candidate >= start_date:
                    add(candidate)
            except ValueError:
                pass
            year_index += 1

    return result
