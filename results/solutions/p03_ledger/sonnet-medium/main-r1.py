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
        t = op.split(' ')
        v = t[0]
        ok = False
        if v == "open" and len(t) == 3:
            n = amt(t[2])
            a = t[1]
            if n is not None and a not in bal:
                bal[a] = n
                stack.append(('b', [(a, None)]))
                ok = True
        elif v == "deposit" and len(t) == 3:
            n = amt(t[2])
            a = t[1]
            if n is not None and n > 0 and a in bal:
                stack.append(('b', [(a, bal[a])]))
                bal[a] += n
                ok = True
        elif v == "withdraw" and len(t) == 3:
            n = amt(t[2])
            a = t[1]
            if (n is not None and n > 0 and a in bal and a not in frozen
                    and bal[a] >= n):
                stack.append(('b', [(a, bal[a])]))
                bal[a] -= n
                ok = True
        elif v == "transfer" and len(t) == 4:
            a, b = t[1], t[2]
            n = amt(t[3])
            if (n is not None and n > 0 and a != b and a in bal and b in bal
                    and a not in frozen and bal[a] >= n):
                stack.append(('b', [(a, bal[a]), (b, bal[b])]))
                bal[a] -= n
                bal[b] += n
                ok = True
        elif v == "freeze" and len(t) == 2:
            a = t[1]
            if a in bal and a not in frozen:
                frozen.add(a)
                stack.append(('f', a, False))
                ok = True
        elif v == "unfreeze" and len(t) == 2:
            a = t[1]
            if a in bal and a in frozen:
                frozen.discard(a)
                stack.append(('f', a, True))
                ok = True
        elif v == "undo" and len(t) == 1:
            if stack:
                rec = stack.pop()
                if rec[0] == 'b':
                    for name, old in reversed(rec[1]):
                        if old is None:
                            del bal[name]
                            frozen.discard(name)
                        else:
                            bal[name] = old
                else:
                    _, name, prev = rec
                    if prev:
                        frozen.add(name)
                    else:
                        frozen.discard(name)
                ok = True
        if not ok:
            rejected.append(i)
    return bal, rejected
