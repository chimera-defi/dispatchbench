"""Per-problem reviewer notes for results/solutions/<problem>/README.md. Written by hand; analysis.export_solutions renders them.
Each entry: pid -> (one-line summary, [approach and trap bullets]). Keep every claim checkable against the problem statement."""
NOTES = {
    "p01_overlap_minutes": ("Total minutes (half-open intervals) covered by at least k meetings at once.", [
        "Sweep line: +1 at each start, -1 at each end, sort events, add the gap length whenever the running count is >= k. O(n log n).",
        "Traps: a meeting ending at t and one starting at t do not overlap; start == end covers nothing; times reach 10**9, so no per-minute loop."]),
    "p02_squash": ("Run-length encode a string; runs of 1-2 are written out, runs of 3+ become count + char; digits and backslash are escaped.", [
        "One pass over maximal runs; run >= 3 gives str(len) + esc(c), shorter runs give esc(c) repeated. O(n) with a list join.",
        "Traps: the escape applies to every written char (also inside short runs); the count itself is never escaped; empty string; `+=` on 200k chars."]),
    "p03_ledger": ("Simulate bank operations with freeze rules and undo; return final balances and the indices of failed ops.", [
        "Dict of balances plus a stack of inverse actions for each successful non-undo op; `undo` pops the stack. O(n).",
        "Traps: amount must be all digits (no sign, `007` ok); open allows 0, other amounts need > 0; deposit and transfer-target may be frozen; failed ops change nothing and are not undoable; failed undo is rejected."]),
    "p04_taller_within": ("For each position, count strictly taller people among the k directly in front.", [
        "Sliding window over the last k values with a Fenwick tree over compressed heights (add a[i], remove a[i-k]); query count greater than a[i]. O(n log n).",
        "Traps: O(n*k) brute force times out at 200k; strict `>`; k = 0 gives all zeros; k larger than the prefix."]),
    "p05_pass_route": ("Cheapest trip from stop 0 to n-1 where zone passes can be bought at listed stations to make that zone's rides free.", [
        "Dijkstra over states (stop, set of bought zones); at most 4 zones so 16 masks. Buying at a station is an edge to the same stop with a bigger mask. About 32k states.",
        "Traps: a pass can only be bought while standing at its station; zone -1 is never free; parallel rides; buying a pass twice; unreachable gives -1."]),
    "p06_calc": ("Evaluate an integer expression with + - * / % ^, unary minus and parentheses; return the int or \"error\".", [
        "Recursive-descent or precedence-climbing parser on Python big ints, with the stated precedence: `^` right-assoc, then unary minus, then `* / %`, then `+ -`.",
        "Traps: `-2^2` is -4 but `2^-1` is an error; `/` truncates toward zero and `%` takes the dividend's sign (not Python `//` and `%`); `0^0` is 1; zero divisor or negative power anywhere is \"error\"; long `--` chains and depth-50 parentheses."]),
    "p07_weighted_distance_sums": ("For every tree node v, sum over nodes u of w[u] * dist(u, v).", [
        "Rerooting: compute S(0) and subtree weights once, then S(child) = S(parent) + W_total - 2 * sub[child]. O(n).",
        "Traps: n = 200000 path breaks recursive DFS (use an iterative order); O(n^2) all-pairs is too slow."]),
    "p08_recur": ("Expand a calendar recurrence rule (daily, weekly, monthly by day or by nth weekday, yearly) into the first count dates.", [
        "Generate candidates per rule with `datetime`/`calendar` and keep those >= start: step K days; active weeks counted from the Monday of start's week; active months counted from start's month.",
        "Traps: a month without day D is skipped, never clamped; -1 means last day or last such weekday; a missing 5th weekday contributes nothing; `02-29` only in leap years (1900, 2100, 2200, 2300 are not leap); start itself is included if it matches."]),
    "p09_k_machine_schedule": ("Max total pay of jobs that fit on k identical machines (half-open intervals).", [
        "Min-cost flow: compress times into a line, k units of flow along time edges (cost 0), each job is a start->end edge of capacity 1 and cost -pay.",
        "Traps: greedy by end time or pay is wrong for weighted jobs; a job ending at t and one starting at t may share a machine; times up to 10**9 need compression."]),
    "p10_avoid_count": ("Count length-n strings over a small alphabet that contain no banned substring, mod 1e9+7, with n up to 10**18.", [
        "Build an Aho-Corasick automaton (at most 21 states), mark a state bad if it or any suffix-link ancestor ends a banned word, then raise the transition matrix to the n-th power. O(S^3 log n).",
        "Traps: banned words that contain others or repeat; the bad flag must propagate through failure links; n = 0 gives 1; linear DP over n cannot reach 10**18."]),
    "p11_best_average": ("Largest average over contiguous subarrays of length >= k, as an exact reduced fraction.", [
        "Dinkelbach iteration (or a binary search in exact integer or rational arithmetic, never floats) on the ratio, using prefix sums and a running minimum prefix at distance >= k; the search itself must be exact, not just the final fraction. O(n) per iteration.",
        "Traps: float comparison fails when two averages differ by < 1e-9; the fraction must be in lowest terms; the best subarray can be longer than k."]),
    "p12_sheet": ("Evaluate a spreadsheet of integers and formulas (SUM/MIN/MAX/IF, ranges) with #DIV/0! and #CYCLE! errors.", [
        "Recursive-descent formula parser plus memoised evaluation of cells with an in-progress marker; a reference to an in-progress cell yields #CYCLE!.",
        "Traps: strict left-to-right error order; IF evaluates only the chosen branch; ranges skip missing cells but a missing-cell formula argument counts as 0; truncating division; reference chains up to 2574 deep exceed Python's default recursion limit."]),
    "p13_xor_ring": ("Apply a XOR-of-offsets update to a ring of lamps t times (t up to 10**18).", [
        "The step is multiplication by a polynomial in GF(2)[x]/(x^n - 1); square-and-multiply the polynomial (carry-less multiply on Python ints) and apply it once. About 60 squarings.",
        "Traps: reduce negative or huge offsets mod n; duplicate offsets cancel; direction is `(i + d) mod n`; t = 0 returns the input; simulating t steps is impossible."]),
    "p14_bounce_board": ("Expected number of turns to finish a dice board with bounce-back and jumps, as an exact fraction, or None if the game may never end.", [
        "Resolve jump chains into a transition table, find states reachable from 0 that cannot reach cell n (then answer None), and solve E = 1 + P*E by Gaussian elimination with `Fraction`s.",
        "Traps: bounce formula `2n - p - r`; jumps within the same turn; non-termination must be decided by graph reachability, not by a float result; reduce the fraction."]),
    "p15_paint_erase": ("Apply paint-if-not-darker and erase operations to a strip of up to 10**9 cells; report cell counts per colour.", [
        "Compress coordinates from all l and r+1, then a segment tree with lazy `chmax(c)` for paint and `assign blank` for erase; read the leaves at the end, weighting by segment length.",
        "Traps: a plain interval map degrades to O(n^2) because higher colours are never removed; blank counts as lower than every colour; erase wins over earlier paint; n is too large for an array."]),
    "fizzbuzz": ("Return 1..n as strings, with Fizz, Buzz and FizzBuzz for multiples of 3, 5 and 15.", [
        "Loop 1..n; test 15 (or build \"Fizz\"+\"Buzz\") before 3 and 5. O(n).",
        "Traps: check order, 1-indexing, strings not ints."]),
    "course2": ("Course Schedule II: return a valid order of courses given prerequisites, or [] if there is a cycle.", [
        "Topological sort (Kahn's algorithm, or DFS with three colours). O(V + E).",
        "Traps: `[a, b]` means b before a; a cycle must give []; up to ~4M edges and recursion depth 2000 for DFS."]),
    "candy": ("Candy: minimum candies so each child gets at least one and a higher rating than a neighbour gets more.", [
        "Two passes: left to right (rating up gives prev + 1), right to left (rating up gives next + 1), take the per-child max and sum. O(n).",
        "Traps: equal ratings impose no constraint; a single pass is not enough; the answer is the sum of maxima, not of either pass."]),
    "itinerary": ("Reconstruct Itinerary: use every ticket once from JFK, lexically smallest itinerary.", [
        "Hierholzer's algorithm with neighbours kept in sorted order (heap): DFS, append airport after its edges are used, reverse. O(E log E).",
        "Traps: plain greedy DFS gets stuck in dead ends; duplicate tickets; must use all tickets."]),
    "minwindow": ("Minimum Window Substring: shortest substring of s containing every character of t with multiplicity.", [
        "Sliding window with a need-count map and a formed counter; expand right, shrink left while valid. O(m + n).",
        "Traps: duplicates in t; case-sensitive; return \"\" when no window exists; 10**5 length rules out O(n^2)."]),
    "wildcard": ("Wildcard Matching: does pattern p with ? and * match all of s?", [
        "O(m*n) DP, or greedy two pointers that remember the last `*` and backtrack to it.",
        "Traps: `*` may match empty; consecutive and trailing stars; empty s or p; plain recursion is exponential."]),
}
