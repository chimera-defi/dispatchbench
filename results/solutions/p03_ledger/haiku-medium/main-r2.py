def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    DIGITS = "0123456789"
    accounts: dict[str, list] = {}  # name -> [balance, frozen]
    history: list[tuple] = []  # undo records for successful non-undo operations
    rejected: list[int] = []

    def amount(tok: str):
        if tok and all(c in DIGITS for c in tok):
            return int(tok)
        return None

    for idx, op in enumerate(ops):
        t = op.split(" ")
        verb = t[0]
        record = None  # None means the operation failed

        if verb == "open" and len(t) == 3:
            name, n = t[1], amount(t[2])
            if n is not None and name not in accounts:
                accounts[name] = [n, False]
                record = ("open", name)

        elif verb == "deposit" and len(t) == 3:
            name, n = t[1], amount(t[2])
            if n is not None and n > 0 and name in accounts:
                accounts[name][0] += n
                record = ("bal", name, -n)

        elif verb == "withdraw" and len(t) == 3:
            name, n = t[1], amount(t[2])
            if n is not None and n > 0 and name in accounts:
                acc = accounts[name]
                if not acc[1] and acc[0] >= n:
                    acc[0] -= n
                    record = ("bal", name, n)

        elif verb == "transfer" and len(t) == 4:
            src, dst, n = t[1], t[2], amount(t[3])
            if (n is not None and n > 0 and src != dst
                    and src in accounts and dst in accounts):
                a = accounts[src]
                if not a[1] and a[0] >= n:
                    a[0] -= n
                    accounts[dst][0] += n
                    record = ("xfer", src, dst, n)

        elif verb == "freeze" and len(t) == 2:
            name = t[1]
            if name in accounts and not accounts[name][1]:
                accounts[name][1] = True
                record = ("frz", name, False)  # previous frozen state

        elif verb == "unfreeze" and len(t) == 2:
            name = t[1]
            if name in accounts and accounts[name][1]:
                accounts[name][1] = False
                record = ("frz", name, True)  # previous frozen state

        elif verb == "undo" and len(t) == 1 and history:
            rec = history.pop()
            kind = rec[0]
            if kind == "open":
                del accounts[rec[1]]
            elif kind == "bal":
                accounts[rec[1]][0] += rec[2]
            elif kind == "xfer":
                _, src, dst, n = rec
                accounts[src][0] += n
                accounts[dst][0] -= n
            elif kind == "frz":
                accounts[rec[1]][1] = rec[2]
            continue  # undo operations are never recorded

        if record is None:
            rejected.append(idx)
        else:
            history.append(record)

    balances = {name: acc[0] for name, acc in accounts.items()}
    return balances, rejected
