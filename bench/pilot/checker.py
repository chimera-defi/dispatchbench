"""Hidden checker: python3 -I checker.py <problem> <candidate.py>. Prints JSON {pass, cases, failed, detail}."""
import json, random, runpy, sys, collections, re, signal, heapq

def ref_fizz(n):
    return ["FizzBuzz" if i % 15 == 0 else "Fizz" if i % 3 == 0 else "Buzz" if i % 5 == 0 else str(i) for i in range(1, n + 1)]

def ref_candy(r):  # brute-force-ish relaxation (independent of two-pass greedy)
    c = [1] * len(r); changed = True
    while changed:
        changed = False
        for i in range(len(r)):
            if i > 0 and r[i] > r[i-1] and c[i] <= c[i-1]: c[i] = c[i-1] + 1; changed = True
            if i + 1 < len(r) and r[i] > r[i+1] and c[i] <= c[i+1]: c[i] = c[i+1] + 1; changed = True
    return sum(c)

def has_cycle(n, pre):
    indeg = [0]*n; g = collections.defaultdict(list)
    for a, b in pre: g[b].append(a); indeg[a] += 1
    q = [i for i in range(n) if indeg[i] == 0]; seen = 0
    while q:
        u = q.pop(); seen += 1
        for v in g[u]:
            indeg[v] -= 1
            if indeg[v] == 0: q.append(v)
    return seen != n

def check_course(n, pre, out):
    if has_cycle(n, pre): return out == []
    if not isinstance(out, list) or sorted(out) != list(range(n)): return False
    pos = {c: i for i, c in enumerate(out)}
    return all(pos[b] < pos[a] for a, b in pre)

# ---- round 2 references ----
def ref_itin_brute(tickets):  # backtracking over sorted edges: first complete path = lexically smallest
    adj = collections.defaultdict(list)
    for a, b in sorted(tickets): adj[a].append(b)
    used = {a: [False]*len(v) for a, v in adj.items()}; path = ["JFK"]; n = len(tickets)
    def dfs(u):
        if len(path) == n + 1: return True
        for i, v in enumerate(adj.get(u, [])):
            if used[u][i] or (i > 0 and adj[u][i-1] == v and not used[u][i-1]): continue
            used[u][i] = True; path.append(v)
            if dfs(v): return True
            used[u][i] = False; path.pop()
        return False
    dfs("JFK"); return path

def ref_itin_hier(tickets):
    adj = collections.defaultdict(list)
    for a, b in tickets: heapq.heappush(adj[a], b)
    out = []; st = ["JFK"]
    while st:
        while adj[st[-1]]: st.append(heapq.heappop(adj[st[-1]]))
        out.append(st.pop())
    return out[::-1]

def check_minwin(s, t, out):
    need = collections.Counter(t)
    def ok(w): c = collections.Counter(w); return all(c[k] >= v for k, v in need.items())
    # reference min length via sliding window
    have = collections.Counter(); missing = len(t); best = None; l = 0
    for r, ch in enumerate(s):
        if need[ch] > 0 and have[ch] < need[ch]: missing -= 1
        have[ch] += 1
        while missing == 0:
            if best is None or r - l + 1 < best: best = r - l + 1
            have[s[l]] -= 1
            if need[s[l]] > 0 and have[s[l]] < need[s[l]]: missing += 1
            l += 1
    if best is None: return out == ""
    return isinstance(out, str) and len(out) == best and out in s and ok(out)

def ref_wild(s, p):
    if len(s) * len(p) <= 400:
        return re.fullmatch("".join(".*" if c == "*" else "." if c == "?" else c for c in p), s, re.S) is not None
    prev = [True] + [False]*len(s)  # DP over pattern
    for c in p:
        cur = [False]*(len(s)+1)
        if c == "*":
            run = False
            for j in range(len(s)+1): run = run or prev[j]; cur[j] = run
        else:
            for j in range(1, len(s)+1): cur[j] = prev[j-1] and (c == "?" or c == s[j-1])
        prev = cur
    return prev[-1]

def gen_itin(rng, k, airports):
    cur = "JFK"; t = []
    for _ in range(k):
        nxt = rng.choice([a for a in airports if a != cur]); t.append([cur, nxt]); cur = nxt
    rng.shuffle(t); return t

def cases(prob, rng):
    if prob == "itinerary":
        cs = [[[["MUC","LHR"],["JFK","MUC"],["SFO","SJC"],["LHR","SFO"]]],
              [[["JFK","SFO"],["JFK","ATL"],["SFO","ATL"],["ATL","JFK"],["ATL","SFO"]]],
              [[["JFK","KUL"],["JFK","NRT"],["NRT","JFK"]]],  # dead-end trap: lexical-first KUL is a dead end
              [[["JFK","AAA"]]], [[["JFK","AAA"],["AAA","JFK"],["JFK","AAA"],["AAA","JFK"]]]]
        for _ in range(30):
            cs.append([gen_itin(rng, rng.randint(1, 9), ["JFK","AAA","AAB","BBB","KUL","NRT"][:rng.randint(2, 6)])])
        cs.append([gen_itin(rng, 300, ["JFK","ATL","SFO","LAX","ORD","DFW","SEA","BOS"])])
        return cs
    if prob == "minwindow":
        cs = [["ADOBECODEBANC", "ABC"], ["a", "a"], ["a", "aa"], ["ab", "b"], ["aa", "aa"], ["abc", "d"], ["bba", "ab"], ["aaflslflsldkalskaaa", "aaa"]]
        for _ in range(30):
            al = rng.choice(["ab", "abc", "aAbB", "abcdefghijk"])
            cs.append(["".join(rng.choice(al) for _ in range(rng.randint(1, 40))), "".join(rng.choice(al) for _ in range(rng.randint(1, 5)))])
        big = "".join(rng.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(100000))
        cs.append([big, "XYZxyzQq"]); cs.append(["a"*99999 + "b", "ab"])
        return cs
    if prob == "wildcard":
        cs = [["aa", "a"], ["aa", "*"], ["cb", "?a"], ["adceb", "*a*b"], ["acdcb", "a*c?b"], ["", ""], ["", "*"], ["", "?"], ["a", ""], ["abc", "***"], ["abcd", "a**d"], ["mississippi", "m??*ss*?i*pi"]]
        for _ in range(30):
            s = "".join(rng.choice("ab") for _ in range(rng.randint(0, 12)))
            p = "".join(rng.choice("ab?**") for _ in range(rng.randint(0, 10)))
            cs.append([s, p])
        cs.append(["a"*2000, "*a*a*a*a*a*a*a*a*a*a*a*a*b"])   # exponential-backtracking trap
        cs.append(["ab"*1000, "*ab*ab*ab*" + "?"*1000])
        cs.append(["a"*1500 + "b", "*" * 500 + "a"*10 + "*b"])
        return cs
    if prob == "fizzbuzz":
        return [[n] for n in [1, 2, 3, 5, 15, 30, 10000] + [rng.randint(1, 500) for _ in range(30)]]
    if prob == "candy":
        cs = [[[0]], [[1, 2]], [[2, 1]], [[1, 1, 1]], [[1, 0, 2]], [[1, 2, 2]], [[1, 3, 2, 2, 1]],
              [[5, 4, 3, 2, 1]], [[1, 2, 3, 4, 5]], [[1, 3, 4, 5, 2]]]
        cs += [[[rng.randint(0, rng.choice([2, 5, 20000])) for _ in range(rng.randint(1, 60))]] for _ in range(30)]
        return cs
    if prob == "course2":
        cs = [[1, []], [2, [[1, 0]]], [2, [[1, 0], [0, 1]]], [4, [[1, 0], [2, 0], [3, 1], [3, 2]]], [3, []],
              [3, [[0, 1], [1, 2], [2, 0]]], [5, [[1, 0], [2, 1], [2, 2 - 2]]]]
        for _ in range(30):
            n = rng.randint(1, 40); perm = list(range(n)); rng.shuffle(perm); pre = set()
            for _ in range(rng.randint(0, n * 2)):
                i, j = rng.randrange(n), rng.randrange(n)
                if i == j: continue
                if i > j: i, j = j, i
                pre.add((perm[j], perm[i]))  # DAG
            pre = [list(p) for p in pre]
            if rng.random() < 0.3 and n > 1:  # inject a back edge -> likely cycle
                a, b = rng.sample(range(n), 2); 
                if [a, b] not in pre and [b, a] not in pre: pre.append([b, a]); pre.append([a, b])
            cs.append([n, pre])
        big = list(range(2000)); cs.append([2000, [[big[i+1], big[i]] for i in range(1999)]])
        return cs

def main():
    prob, path = sys.argv[1], sys.argv[2]
    ns = runpy.run_path(path)
    fn = ns[{"fizzbuzz": "fizzBuzz", "course2": "findOrder", "candy": "candy", "itinerary": "findItinerary", "minwindow": "minWindow", "wildcard": "isMatch"}[prob]]
    def _alarm(*a): raise TimeoutError("case > 10s")
    signal.signal(signal.SIGALRM, _alarm)
    rng = random.Random(1234); cs = cases(prob, rng); failed = 0; detail = None
    for args in cs:
        try:
            signal.alarm(10)
            out = fn(*[json.loads(json.dumps(a)) for a in args])
            signal.alarm(0)
            if prob == "fizzbuzz": ok = out == ref_fizz(*args)
            elif prob == "candy": ok = out == ref_candy(*args)
            elif prob == "course2": ok = check_course(args[0], args[1], out)
            elif prob == "itinerary": ok = out == (ref_itin_brute(*args) if len(args[0]) <= 12 else ref_itin_hier(*args))
            elif prob == "minwindow": ok = check_minwin(args[0], args[1], out)
            elif prob == "wildcard": ok = out is ref_wild(*args) or out == ref_wild(*args)
        except BaseException as e:
            signal.alarm(0); ok = False; out = repr(e)
        if not ok:
            failed += 1
            if detail is None: detail = f"args={str(args)[:200]} got={str(out)[:200]}"
    print(json.dumps({"pass": failed == 0, "cases": len(cs), "failed": failed, "detail": detail}))

main()
