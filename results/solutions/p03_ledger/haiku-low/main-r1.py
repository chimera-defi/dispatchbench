def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts = {}  # name -> [balance, frozen]
    history = []   # revert records for successful non-undo operations
    rejected = []

    def parse_amount(s):
        if s == "" or any(c not in "0123456789" for c in s):
            return None
        return int(s)

    def revert(rec):
        kind = rec[0]
        if kind == "del":
            del accounts[rec[1]]
        elif kind == "bal":
            for name, delta in rec[1]:
                accounts[name][0] += delta
        elif kind == "frz":
            accounts[rec[1]][1] = rec[2]

    for i, op in enumerate(ops):
        t = op.split(" ")
        verb = t[0]
        rec = None

        if verb == "undo":
            if len(t) == 1 and history:
                revert(history.pop())
            else:
                rejected.append(i)
            continue

        if verb == "open" and len(t) == 3:
            n = parse_amount(t[2])
            if n is not None and t[1] not in accounts:
                accounts[t[1]] = [n, False]
                rec = ("del", t[1])

        elif verb == "deposit" and len(t) == 3:
            n = parse_amount(t[2])
            if n is not None and n > 0 and t[1] in accounts:
                accounts[t[1]][0] += n
                rec = ("bal", [(t[1], -n)])

        elif verb == "withdraw" and len(t) == 3:
            n = parse_amount(t[2])
            if n is not None and n > 0 and t[1] in accounts:
                acc = accounts[t[1]]
                if not acc[1] and acc[0] >= n:
                    acc[0] -= n
                    rec = ("bal", [(t[1], n)])

        elif verb == "transfer" and len(t) == 4:
            n = parse_amount(t[3])
            a, b = t[1], t[2]
            if (n is not None and n > 0 and a != b
                    and a in accounts and b in accounts):
                src = accounts[a]
                if not src[1] and src[0] >= n:
                    src[0] -= n
                    accounts[b][0] += n
                    rec = ("bal", [(a, n), (b, -n)])

        elif verb == "freeze" and len(t) == 2:
            if t[1] in accounts and not accounts[t[1]][1]:
                accounts[t[1]][1] = True
                rec = ("frz", t[1], False)

        elif verb == "unfreeze" and len(t) == 2:
            if t[1] in accounts and accounts[t[1]][1]:
                accounts[t[1]][1] = False
                rec = ("frz", t[1], True)

        if rec is None:
            rejected.append(i)
        else:
            history.append(rec)

    balances = {name: acc[0] for name, acc in accounts.items()}
    return balances, rejected
