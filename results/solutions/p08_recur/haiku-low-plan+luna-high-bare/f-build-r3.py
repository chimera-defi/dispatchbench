from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    anchor = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    k = int(parts[1])
    result = []

    def emit(candidate):
        if candidate >= anchor:
            result.append(candidate.isoformat())
            return len(result) == count
        return False

    if kind == "DAILY":
        step = timedelta(days=k)
        current = anchor
        while len(result) < count:
            emit(current)
            current += step

    elif kind == "WEEKLY":
        weekdays = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                    "FR": 4, "SA": 5, "SU": 6}
        days = sorted(weekdays[d] for d in parts[2].split(","))
        monday = anchor - timedelta(days=anchor.weekday())
        week_index = 0
        while len(result) < count:
            week_start = monday + timedelta(weeks=week_index)
            for weekday in days:
                if emit(week_start + timedelta(days=weekday)):
                    break
            week_index += k

    elif kind == "MONTHLY":
        y0, m0 = anchor.year, anchor.month
        month_index = 0

        while len(result) < count:
            total_month = (m0 - 1) + month_index
            year = y0 + total_month // 12
            month = total_month % 12 + 1
            _, last_day = calendar.monthrange(year, month)

            if len(parts) == 3:
                day = int(parts[2])
                if day == -1:
                    day = last_day
                if day <= last_day:
                    emit(date(year, month, day))
            else:
                n = int(parts[2])
                weekday = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                           "FR": 4, "SA": 5, "SU": 6}[parts[3]]
                if n == -1:
                    candidate_day = last_day - (
                        date(year, month, last_day).weekday() - weekday
                    ) % 7
                else:
                    first_day = date(year, month, 1)
                    candidate_day = 1 + (weekday - first_day.weekday()) % 7 + 7 * (n - 1)

                if candidate_day <= last_day:
                    emit(date(year, month, candidate_day))

            month_index += k

    elif kind == "YEARLY":
        month, day = map(int, parts[2].split("-"))
        year = anchor.year
        while len(result) < count:
            try:
                emit(date(year, month, day))
            except ValueError:
                pass
            year += k

    return result
