from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    result = []

    if kind == "DAILY":
        step = int(parts[1])
        current = start_date
        for _ in range(count):
            result.append(current.isoformat())
            current += timedelta(days=step)
        return result

    if kind == "WEEKLY":
        step = int(parts[1])
        weekday_codes = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                         "FR": 4, "SA": 5, "SU": 6}
        weekdays = sorted(weekday_codes[x] for x in parts[2].split(","))
        week_start = start_date - timedelta(days=start_date.weekday())
        week_index = 0

        while len(result) < count:
            if week_index % step == 0:
                for weekday in weekdays:
                    current = week_start + timedelta(days=weekday)
                    if current >= start_date:
                        result.append(current.isoformat())
                        if len(result) == count:
                            break
            week_start += timedelta(days=7)
            week_index += 1
        return result

    if kind == "MONTHLY":
        step = int(parts[1])
        year, month = start_date.year, start_date.month
        month_index = 0

        while len(result) < count:
            if month_index % step == 0:
                if len(parts) == 3:
                    day_spec = int(parts[2])
                    last_day = calendar.monthrange(year, month)[1]
                    day = last_day if day_spec == -1 else day_spec
                    if day <= last_day:
                        current = date(year, month, day)
                        if current >= start_date:
                            result.append(current.isoformat())
                else:
                    n = int(parts[2])
                    weekday = {
                        "MO": 0, "TU": 1, "WE": 2, "TH": 3,
                        "FR": 4, "SA": 5, "SU": 6
                    }[parts[3]]
                    last_day = calendar.monthrange(year, month)[1]

                    if n == -1:
                        current = date(year, month, last_day)
                        current -= timedelta(days=(current.weekday() - weekday) % 7)
                    else:
                        first = date(year, month, 1)
                        current = first + timedelta(
                            days=(weekday - first.weekday()) % 7 + 7 * (n - 1)
                        )
                        if current.month != month:
                            current = None

                    if current is not None and current >= start_date:
                        result.append(current.isoformat())

            month += step
            year += (month - 1) // 12
            month = (month - 1) % 12 + 1
            month_index += step

        return result

    if kind == "YEARLY":
        step = int(parts[1])
        target_month, target_day = map(int, parts[2].split("-"))
        year = start_date.year

        while len(result) < count:
            try:
                current = date(year, target_month, target_day)
            except ValueError:
                current = None

            if current is not None and current >= start_date:
                result.append(current.isoformat())

            year += step

        return result
