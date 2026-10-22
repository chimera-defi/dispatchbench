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
            a = t[1]
            if n is not None and a not in bal:
                bal[a] = n
                stack.append(("open", a))
                ok = True
        elif v == "deposit" and len(t) == 3:
            n = amt(t[2])
            a = t[1]
            if n is not None and n > 0 and a in bal:
                bal[a] += n
                stack.append(("deposit", a, n))
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
            a = t[1]
            if a in bal and a not in frozen:
                frozen.add(a)
                stack.append(("freeze", a))
                ok = True
        elif v == "unfreeze" and len(t) == 2:
            a = t[1]
            if a in bal and a in frozen:
                frozen.discard(a)
                stack.append(("unfreeze", a))
                ok = True
        elif v == "undo" and len(t) == 1:
            if stack:
                r = stack.pop()
                k = r[0]
                if k == "open":
                    del bal[r[1]]
                    frozen.discard(r[1])
                elif k == "deposit":
                    bal[r[1]] -= r[2]
                elif k == "withdraw":
                    bal[r[1]] += r[2]
                elif k == "transfer":
                    bal[r[1]] += r[3]
                    bal[r[2]] -= r[3]
                elif k == "freeze":
                    frozen.discard(r[1])
                elif k == "unfreeze":
                    frozen.add(r[1])
                ok = True
        if not ok:
            rejected.append(i)
    return bal, rejected
