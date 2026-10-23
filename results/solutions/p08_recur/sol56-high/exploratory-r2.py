from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    frequency = parts[0]
    interval = int(parts[1])

    weekdays = {
        "MO": 0, "TU": 1, "WE": 2, "TH": 3,
        "FR": 4, "SA": 5, "SU": 6,
    }

    def matches(current: date) -> bool:
        if frequency == "DAILY":
            return (current - start_date).days % interval == 0

        if frequency == "WEEKLY":
            week_start = start_date - timedelta(days=start_date.weekday())
            week_index = (current - week_start).days // 7
            allowed = {weekdays[code] for code in parts[2].split(",")}
            return week_index % interval == 0 and current.weekday() in allowed

        if frequency == "MONTHLY":
            month_index = (
                (current.year - start_date.year) * 12
                + current.month - start_date.month
            )
            if month_index % interval != 0:
                return False

            if len(parts) == 3:
                day_number = int(parts[2])
                if day_number == -1:
                    return current.day == calendar.monthrange(
                        current.year, current.month
                    )[1]
                return current.day == day_number

            ordinal = int(parts[2])
            target_weekday = weekdays[parts[3]]

            if current.weekday() != target_weekday:
                return False

            if ordinal == -1:
                return current.day + 7 > calendar.monthrange(
                    current.year, current.month
                )[1]

            return (current.day - 1) // 7 + 1 == ordinal

        year_index = current.year - start_date.year
        if year_index % interval != 0:
            return False

        month, day = map(int, parts[2].split("-"))
        return current.month == month and current.day == day

    result = []
    current = start_date

    while len(result) < count:
        if matches(current):
            result.append(current.isoformat())
        current += timedelta(days=1)

    return result
