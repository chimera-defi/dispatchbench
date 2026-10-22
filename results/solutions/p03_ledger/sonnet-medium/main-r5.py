def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    bal = {}
    frozen = set()
    stack = []
    rejected = []
    digits = set("0123456789")

    def amt(s):
        if s and all(c in digits for c in s):
            return int(s)
        return None

    for i, op in enumerate(ops):
        t = op.split(" ")
        v = t[0]
        ok = False
        if v == "open" and len(t) == 3:
            n = amt(t[2])
            if n is not None and t[1] not in bal:
                bal[t[1]] = n
                stack.append(("open", t[1]))
                ok = True
        elif v == "deposit" and len(t) == 3:
            n = amt(t[2])
            if n is not None and n > 0 and t[1] in bal:
                bal[t[1]] += n
                stack.append(("deposit", t[1], n))
                ok = True
        elif v == "withdraw" and len(t) == 3:
            n = amt(t[2])
            a = t[1]
            if n is not None and n > 0 and a in bal and a not in frozen and bal[a] >= n:
                bal[a] -= n
                stack.append(("withdraw", a, n))
                ok = True
        elif v == "transfer" and len(t) == 4:
            n = amt(t[3])
            a, b = t[1], t[2]
            if (n is not None and n > 0 and a != b and a in bal and b in bal
                    and a not in frozen and bal[a] >= n):
                bal[a] -= n
                bal[b] += n
                stack.append(("transfer", a, b, n))
                ok = True
        elif v == "freeze" and len(t) == 2:
            if t[1] in bal and t[1] not in frozen:
                frozen.add(t[1])
                stack.append(("freeze", t[1]))
                ok = True
        elif v == "unfreeze" and len(t) == 2:
            if t[1] in bal and t[1] in frozen:
                frozen.discard(t[1])
                stack.append(("unfreeze", t[1]))
                ok = True
        elif v == "undo" and len(t) == 1:
            if stack:
                e = stack.pop()
                k = e[0]
                if k == "open":
                    del bal[e[1]]
                    frozen.discard(e[1])
                elif k == "deposit":
                    bal[e[1]] -= e[2]
                elif k == "withdraw":
                    bal[e[1]] += e[2]
                elif k == "transfer":
                    bal[e[1]] += e[3]
                    bal[e[2]] -= e[3]
                elif k == "freeze":
                    frozen.discard(e[1])
                elif k == "unfreeze":
                    frozen.add(e[1])
                ok = True
        if not ok:
            rejected.append(i)
    return bal, rejected
