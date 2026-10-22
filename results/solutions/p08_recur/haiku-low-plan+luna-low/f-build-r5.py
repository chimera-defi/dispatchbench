from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    k = int(parts[1])
    result = []

    if kind == "DAILY":
        for i in range(count):
            result.append((start_date + timedelta(days=i * k)).isoformat())
        return result

    if kind == "WEEKLY":
        weekdays = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                    "FR": 4, "SA": 5, "SU": 6}
        days = sorted(weekdays[code] for code in parts[2].split(","))
        monday = start_date - timedelta(days=start_date.weekday())
        week = 0
        while len(result) < count:
            base = monday + timedelta(days=7 * week)
            for weekday in days:
                candidate = base + timedelta(days=weekday)
                if candidate >= start_date:
                    result.append(candidate.isoformat())
                    if len(result) == count:
                        return result
            week += k
        return result

    if kind == "MONTHLY":
        month_index = start_date.year * 12 + start_date.month - 1
        if len(parts) == 3:
            day = int(parts[2])
            for offset in range(0, 12000, k):
                current = month_index + offset
                year, month0 = divmod(current, 12)
                month = month0 + 1
                last_day = calendar.monthrange(year, month)[1]
                candidate_day = last_day if day == -1 else day
                if candidate_day <= last_day:
                    candidate = date(year, month, candidate_day)
                    if candidate >= start_date:
                        result.append(candidate.isoformat())
                        if len(result) == count:
                            return result
        else:
            n = int(parts[2])
            weekday = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                       "FR": 4, "SA": 5, "SU": 6}[parts[3]]
            for offset in range(0, 12000, k):
                current = month_index + offset
                year, month0 = divmod(current, 12)
                month = month0 + 1
                last_day = calendar.monthrange(year, month)[1]
                if n == -1:
                    day = last_day - (
                        date(year, month, last_day).weekday() - weekday
                    ) % 7
                else:
                    first_day_weekday = date(year, month, 1).weekday()
                    day = 1 + (weekday - first_day_weekday) % 7 + 7 * (n - 1)
                if day <= last_day:
                    candidate = date(year, month, day)
                    if candidate >= start_date:
                        result.append(candidate.isoformat())
                        if len(result) == count:
                            return result
        return result

    if kind == "YEARLY":
        month, day = map(int, parts[2].split("-"))
        for year in range(start_date.year, 3000, k):
            try:
                candidate = date(year, month, day)
            except ValueError:
                continue
            if candidate >= start_date:
                result.append(candidate.isoformat())
                if len(result) == count:
                    return result
        return result

    return result
