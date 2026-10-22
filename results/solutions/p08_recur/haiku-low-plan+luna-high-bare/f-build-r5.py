from datetime import date, timedelta
import calendar


def recur(start: str, rule: str, count: int) -> list[str]:
    start_date = date.fromisoformat(start)
    parts = rule.split()
    kind = parts[0]
    k = int(parts[1])
    results = []

    def add(candidate):
        if candidate >= start_date:
            results.append(candidate.isoformat())

    if kind == "DAILY":
        for i in range(count):
            results.append((start_date + timedelta(days=i * k)).isoformat())

    elif kind == "WEEKLY":
        weekdays = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                    "FR": 4, "SA": 5, "SU": 6}
        days = sorted(weekdays[d] for d in parts[2].split(","))
        monday = start_date - timedelta(days=start_date.weekday())
        for week in range(0, 3000 * 53, k):
            base = monday + timedelta(weeks=week)
            if base.year >= 3000:
                break
            for weekday in days:
                add(base + timedelta(days=weekday))
                if len(results) == count:
                    return results

    elif kind == "MONTHLY":
        first_month = start_date.year * 12 + start_date.month - 1
        if len(parts) == 3:
            day = int(parts[2])
            for offset in range(0, 1200 * 12, k):
                total = first_month + offset
                year, month0 = divmod(total, 12)
                if year >= 3000:
                    break
                month = month0 + 1
                last = calendar.monthrange(year, month)[1]
                candidate_day = last if day == -1 else day
                if candidate_day <= last:
                    add(date(year, month, candidate_day))
                    if len(results) == count:
                        return results
        else:
            n = int(parts[2])
            weekday = {"MO": 0, "TU": 1, "WE": 2, "TH": 3,
                       "FR": 4, "SA": 5, "SU": 6}[parts[3]]
            for offset in range(0, 1200 * 12, k):
                total = first_month + offset
                year, month0 = divmod(total, 12)
                if year >= 3000:
                    break
                month = month0 + 1
                last = calendar.monthrange(year, month)[1]
                if n == -1:
                    candidate_day = last - ((date(year, month, last).weekday() - weekday) % 7)
                else:
                    first = 1 + ((weekday - date(year, month, 1).weekday()) % 7)
                    candidate_day = first + 7 * (n - 1)
                if candidate_day <= last:
                    add(date(year, month, candidate_day))
                    if len(results) == count:
                        return results

    elif kind == "YEARLY":
        month, day = map(int, parts[2].split("-"))
        for year in range(start_date.year, 3000, k):
            try:
                add(date(year, month, day))
            except ValueError:
                pass
            if len(results) == count:
                return results

    return results[:count]
