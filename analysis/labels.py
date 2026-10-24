"""Names shown to readers, shared by the page, the charts and the tables so every place reads the same.

Problems are "p12 sheet (L6)": number, short name, rung. Fast-mode configs carry a lightning suffix ("sol61-high ⚡").
Sets (use these names everywhere):
  main ladder  p01-p12, rungs L1-L6, two problems per rung, every config
  L7 set       p13-p15, three extra-hard problems, run on a subset of configs
  rescue set   seven main-ladder problems (p03, p04, p08-p12) picked after the main ladder because luna-low fails them most;
               used for the pipeline and repair arms"""
import html

# What each problem tests, one line each. Used as the hover text wherever a problem is named.
TESTS = {
    "p01_overlap_minutes": "minutes with at least k meetings at once; half-open intervals, sweep line",
    "p02_squash": "run-length encoding with escaped digits and backslashes",
    "p03_ledger": "bank operations with validation rules, frozen accounts and transfers",
    "p04_taller_within": "count taller people among the k in front; sliding window",
    "p05_pass_route": "cheapest route when zone passes can be bought on the way; state-space shortest path",
    "p06_calc": "integer expression parser: precedence, right-assoc power, unary minus, errors",
    "p07_weighted_distance_sums": "weighted distance sums from every tree node; rerooting",
    "p08_recur": "calendar recurrence rules (daily, weekly, monthly) expanded to dates",
    "p09_k_machine_schedule": "best total pay for jobs on k printers; weighted interval scheduling",
    "p10_avoid_count": "count strings avoiding banned substrings; automaton DP, modulo",
    "p11_best_average": "largest average of a subarray of length at least k, as an exact fraction",
    "p12_sheet": "spreadsheet evaluator with references, ranges, division and cycle errors",
    "p13_xor_ring": "XOR cellular automaton on a ring for huge t; doubling",
    "p14_bounce_board": "expected turns on a bouncing board game with jumps, as an exact fraction",
    "p15_paint_erase": "paint and erase ranges where higher colours win; segment tree",
}


def pname(p):
    return p.split("_", 1)[1] if "_" in p else p


def pshort(p):
    """"p12 sheet": number and short name, no rung."""
    return f"{p[:3]} {pname(p)}"


def plabel(p, rung=None):
    """Plain text: "p12 sheet (L6)"; the rung is read from the problem's own module when not given."""
    if rung is None: rung = RUNG.get(p[:3])
    return pshort(p) + (f" (L{rung})" if rung else "")


def plabel_html(p, rung=None):
    """The same label with a hover title carrying the one-line description."""
    return f'<span class="pl" title="{html.escape(TESTS.get(p, ""))}">{html.escape(plabel(p, rung))}</span>'


def DISP(c):
    """Display name of a config: fast mode (priority tier) gets a lightning suffix."""
    return c[:-5] + " ⚡" if c.endswith("-fast") else c


# Rung of each problem: 2 per rung, p01-p12 on L1-L6, then p13-p15 on L7.
RUNG = {f"p{i:02d}": (i + 1) // 2 for i in range(1, 13)}
RUNG.update({"p13": 7, "p14": 7, "p15": 7})
