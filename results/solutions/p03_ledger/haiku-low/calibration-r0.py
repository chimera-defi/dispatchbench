def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts = {}  # name -> [balance, frozen]
    history = []   # records of successful non-undo operations, for undo
    rejected = []
    digits = set("0123456789")

    def parse_amount(s):
        if not s or any(c not in digits for c in s):
            return None
        return int(s)

    for i, op in enumerate(ops):
        tok = op.split(" ")
        verb = tok[0]
        ok = False
        record = None

        if verb == "open" and len(tok) == 3:
            name, n = tok[1], parse_amount(tok[2])
            if n is not None and name not in accounts:
                accounts[name] = [n, False]
                record = ("open", name)
                ok = True

        elif verb == "deposit" and len(tok) == 3:
            name, n = tok[1], parse_amount(tok[2])
            if n is not None and n > 0 and name in accounts:
                accounts[name][0] += n
                record = ("bal", name, n)
                ok = True

        elif verb == "withdraw" and len(tok) == 3:
            name, n = tok[1], parse_amount(tok[2])
            if (n is not None and n > 0 and name in accounts
                    and not accounts[name][1] and accounts[name][0] >= n):
                accounts[name][0] -= n
                record = ("bal", name, -n)
                ok = True

        elif verb == "transfer" and len(tok) == 4:
            src, dst, n = tok[1], tok[2], parse_amount(tok[3])
            if (n is not None and n > 0 and src != dst
                    and src in accounts and dst in accounts
                    and not accounts[src][1] and accounts[src][0] >= n):
                accounts[src][0] -= n
                accounts[dst][0] += n
                record = ("transfer", src, dst, n)
                ok = True

        elif verb == "freeze" and len(tok) == 2:
            name = tok[1]
            if name in accounts and not accounts[name][1]:
                accounts[name][1] = True
                record = ("frozen", name, False)
                ok = True

        elif verb == "unfreeze" and len(tok) == 2:
            name = tok[1]
            if name in accounts and accounts[name][1]:
                accounts[name][1] = False
                record = ("frozen", name, True)
                ok = True

        elif verb == "undo" and len(tok) == 1:
            if history:
                rec = history.pop()
                kind = rec[0]
                if kind == "open":
                    del accounts[rec[1]]
                elif kind == "bal":
                    accounts[rec[1]][0] -= rec[2]
                elif kind == "transfer":
                    _, src, dst, n = rec
                    accounts[src][0] += n
                    accounts[dst][0] -= n
                elif kind == "frozen":
                    accounts[rec[1]][1] = rec[2]
                ok = True
            # undo itself is never recorded, so it cannot be reverted

        if ok:
            if record is not None:
                history.append(record)
        else:
            rejected.append(i)

    balances = {name: acc[0] for name, acc in accounts.items()}
    return balances, rejected
