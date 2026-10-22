RUNG = 4
FUNC = "recur"
SIGNATURE = "def recur(start: str, rule: str, count: int) -> list[str]:"
STATEMENT = """\
Expand a calendar recurrence rule. `start` is a date `YYYY-MM-DD`. Return the first `count` dates, in ascending order as `YYYY-MM-DD` strings, that are on or after `start` and match `rule`. `start` itself is included if it matches.

`rule` is one of the forms below. Tokens are separated by single spaces, and `K` is an integer of 1 or more.

- `DAILY K`: `start`, `start + K` days, `start + 2K` days, and so on.
- `WEEKLY K DAYS`: `DAYS` is a comma-separated list of distinct weekday codes from `MO TU WE TH FR SA SU`, in any order. Weeks run Monday to Sunday. Week 0 is the week that contains `start`. Only weeks 0, K, 2K, ... are active, and only the listed weekdays in them match.
- `MONTHLY K D`: `D` is `1`..`31`, or `-1` for the last day of the month. Month 0 is the month of `start`. Only months 0, K, 2K, ... are active. A month that has no day `D` (for example day 31 in April) contributes nothing; the date is not moved to another day.
- `MONTHLY K N WD`: the `N`-th weekday `WD` of each active month, where `N` is `1`..`5`, or `-1` for the last one. A month without a 5th such weekday contributes nothing.
- `YEARLY K MM-DD`: year 0 is the year of `start`. Only years 0, K, 2K, ... are active, each on month `MM`, day `DD`. If the date does not exist in an active year (`02-29` in a non-leap year), that year contributes nothing.

Examples:
- `recur("2026-01-30", "MONTHLY 1 31", 3)` returns `["2026-01-31", "2026-03-31", "2026-05-31"]`.
- `recur("2026-10-22", "WEEKLY 2 MO,FR", 3)` returns `["2026-10-23", "2026-11-02", "2026-11-06"]`.
- `recur("2026-10-22", "MONTHLY 1 -1 FR", 2)` returns `["2026-10-30", "2026-11-27"]`.
- `recur("2023-03-01", "YEARLY 1 02-29", 2)` returns `["2024-02-29", "2028-02-29"]`.

Constraints: `start` is between 1900-01-01 and 2400-12-31, and `1 <= count <= 50`. Every test has `count` matching dates before 3000-01-01."""

import datetime as _dt

_WD = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]


def _mk(y, m, d):
    try:
        return _dt.date(y, m, d)
    except ValueError:
        return None


def _month_day(y, m, D):
    if D == -1:
        nxt = _dt.date(y + (m == 12), m % 12 + 1, 1)
        return nxt - _dt.timedelta(days=1)
    return _mk(y, m, D)


def _nth_wd(y, m, N, wd):
    days = [_dt.date(y, m, d) for d in range(1, 32) if _mk(y, m, d) and _dt.date(y, m, d).weekday() == wd]
    if N == -1: return days[-1]
    return days[N - 1] if N <= len(days) else None


def ref(start, rule, count):
    s = _dt.date.fromisoformat(start); t = rule.split(" "); K = int(t[1]); out = []
    if t[0] == "DAILY":
        return [(s + _dt.timedelta(days=K * i)).isoformat() for i in range(count)]
    if t[0] == "WEEKLY":
        wds = sorted(_WD.index(x) for x in t[2].split(",")); mon = s - _dt.timedelta(days=s.weekday()); wk = 0
        while len(out) < count:
            for wd in wds:
                d = mon + _dt.timedelta(days=7 * wk + wd)
                if d >= s and len(out) < count: out.append(d)
            wk += K
    elif t[0] in ("MONTHLY", "YEARLY"):
        step = 0
        while len(out) < count:
            if t[0] == "YEARLY":
                y = s.year + step; mm, dd = map(int, t[2].split("-")); d = _mk(y, mm, dd) if y <= 9999 else None
            else:
                mi = s.month - 1 + step; y, m = s.year + mi // 12, mi % 12 + 1
                d = _month_day(y, m, int(t[2])) if len(t) == 3 else _nth_wd(y, m, int(t[2]), _WD.index(t[3]))
            if y > 9999: break
            if d is not None and d >= s: out.append(d)
            step += K
    return [d.isoformat() for d in out]


def brute(start, rule, count):
    # Independent: walk forward one day at a time and test each date against the rule.
    s = _dt.date.fromisoformat(start); t = rule.split(" "); K = int(t[1]); out = []; d = s
    mon0 = s.toordinal() - s.weekday()
    while len(out) < count and d.year < 3000:
        if t[0] == "DAILY": ok = (d - s).days % K == 0
        elif t[0] == "WEEKLY": ok = ((d.toordinal() - mon0) // 7) % K == 0 and _WD[d.weekday()] in t[2].split(",")
        elif t[0] == "YEARLY": ok = (d.year - s.year) % K == 0 and d.strftime("%m-%d") == t[2]
        else:
            mi = (d.year - s.year) * 12 + d.month - s.month
            last = (d + _dt.timedelta(days=1)).month != d.month
            if len(t) == 3:
                D = int(t[2]); ok = mi % K == 0 and (d.day == D or (D == -1 and last))
            else:
                N = int(t[2]); same_wd = _WD[d.weekday()] == t[3]
                kth = (d.day - 1) // 7 + 1; is_last = (d + _dt.timedelta(days=7)).month != d.month
                ok = mi % K == 0 and same_wd and (kth == N or (N == -1 and is_last))
        if ok: out.append(d.isoformat())
        d += _dt.timedelta(days=1)
    return out


def _rule(rng):
    f = rng.choice(["DAILY", "WEEKLY", "MONTHLY", "MONTHLY_NTH", "YEARLY"])
    K = rng.choice([1, 1, 2, 3, 5, 12])
    if f == "DAILY": return f"DAILY {rng.choice([1, 2, 7, 30, 400])}"
    if f == "WEEKLY": return f"WEEKLY {K} " + ",".join(rng.sample(_WD, rng.randint(1, 4)))
    if f == "MONTHLY": return f"MONTHLY {K} {rng.choice([1, 15, 28, 29, 30, 31, -1])}"
    if f == "MONTHLY_NTH": return f"MONTHLY {K} {rng.choice([1, 2, 4, 5, -1])} {rng.choice(_WD)}"
    return f"YEARLY {rng.choice([1, 1, 2, 4])} {rng.choice(['01-01', '02-29', '02-28', '12-31', '03-01'])}"


def _case(rng, count_max, horizon_years):
    while True:
        st = _dt.date(1900, 1, 1) + _dt.timedelta(days=rng.randrange(_dt.date(2400, 12, 31).toordinal() - _dt.date(1900, 1, 1).toordinal()))
        r = _rule(rng); c = rng.randint(1, count_max); got = ref(st.isoformat(), r, c)
        if len(got) == c and _dt.date.fromisoformat(got[-1]).year < min(3000, st.year + horizon_years):
            return (st.isoformat(), r, c)


def small(rng):
    return _case(rng, 6, 40)


def fixed():
    return [a for a, _ in EXAMPLES] + [("2024-02-29", "YEARLY 1 02-29", 3), ("2026-10-26", "WEEKLY 1 MO", 2), ("2026-10-25", "WEEKLY 2 MO", 2),
                                       ("1900-02-01", "MONTHLY 1 29", 3), ("2026-01-31", "MONTHLY 1 5 SU", 4), ("2026-12-31", "DAILY 1", 2)]


def big(rng):
    return [_case(rng, 50, 600) for _ in range(40)]


EXAMPLES = [(("2026-01-30", "MONTHLY 1 31", 3), ["2026-01-31", "2026-03-31", "2026-05-31"]),
            (("2026-10-22", "WEEKLY 2 MO,FR", 3), ["2026-10-23", "2026-11-02", "2026-11-06"]),
            (("2026-10-22", "MONTHLY 1 -1 FR", 2), ["2026-10-30", "2026-11-27"]),
            (("2023-03-01", "YEARLY 1 02-29", 2), ["2024-02-29", "2028-02-29"])]

_WRONG_BASE = '''
import datetime as dt, calendar
W = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
def recur(start, rule, count):
    s = dt.date.fromisoformat(start); t = rule.split(" "); K = int(t[1]); out = []
    if t[0] == "DAILY": return [(s + dt.timedelta(days=K * i)).isoformat() for i in range(count)]
    if t[0] == "WEEKLY":
        wds = sorted(W.index(x) for x in t[2].split(",")); anchor = ANCHOR; wk = 0
        while len(out) < count:
            for i in range(7):
                d = anchor + dt.timedelta(days=7 * wk + i)
                if d.weekday() in wds and d >= s and len(out) < count: out.append(d)
            wk += K
        return [d.isoformat() for d in out]
    step = 0
    while len(out) < count and step < 12 * 2000:
        if t[0] == "YEARLY":
            y = s.year + step; mm, dd = map(int, t[2].split("-"))
            if mm == 2 and dd == 29 and not calendar.isleap(y): d = CLAMP_LEAP
            else: d = dt.date(y, mm, dd)
        else:
            mi = s.month - 1 + step; y, m = s.year + mi // 12, mi % 12 + 1; ml = calendar.monthrange(y, m)[1]
            if len(t) == 3:
                D = int(t[2]); D = ml if D == -1 else D
                d = dt.date(y, m, D) if D <= ml else CLAMP_DAY
            else:
                N, wd = int(t[2]), W.index(t[3]); days = [x for x in range(1, ml + 1) if dt.date(y, m, x).weekday() == wd]
                d = dt.date(y, m, days[-1] if N == -1 else days[N - 1]) if N == -1 or N <= len(days) else None
        if d is not None and d >= s: out.append(d)
        step += K
    return [d.isoformat() for d in out]
'''

WRONG = {
    "clamp_to_month_end": _WRONG_BASE.replace("ANCHOR", "s - dt.timedelta(days=s.weekday())").replace("CLAMP_LEAP", "None").replace("CLAMP_DAY", "dt.date(y, m, ml)"),
    "weeks_from_start_date": _WRONG_BASE.replace("ANCHOR", "s").replace("CLAMP_LEAP", "None").replace("CLAMP_DAY", "None"),
    "leap_day_to_feb_28": _WRONG_BASE.replace("ANCHOR", "s - dt.timedelta(days=s.weekday())").replace("CLAMP_LEAP", "dt.date(y, 2, 28)").replace("CLAMP_DAY", "None"),
}
