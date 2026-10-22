def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    balances: dict[str, int] = {}
    frozen: set[str] = set()
    history: list[tuple] = []  # undo records for successful non-undo operations
    rejected: list[int] = []

    def valid_amount(tok: str) -> bool:
        return len(tok) > 0 and all(c in "0123456789" for c in tok)

    for i, op in enumerate(ops):
        parts = op.split(" ")
        if any(p == "" for p in parts):
            rejected.append(i)
            continue

        verb, args = parts[0], parts[1:]
        ok = False
        record = None

        if verb == "open" and len(args) == 2:
            a, n = args
            if valid_amount(n) and a not in balances:
                amt = int(n)
                balances[a] = amt
                record = ("delete", a)
                ok = True

        elif verb == "deposit" and len(args) == 2:
            a, n = args
            if valid_amount(n) and a in balances and int(n) > 0:
                amt = int(n)
                balances[a] += amt
                record = ("adjust", [(a, amt)])
                ok = True

        elif verb == "withdraw" and len(args) == 2:
            a, n = args
            if (valid_amount(n) and a in balances and a not in frozen
                    and int(n) > 0 and balances[a] >= int(n)):
                amt = int(n)
                balances[a] -= amt
                record = ("adjust", [(a, -amt)])
                ok = True

        elif verb == "transfer" and len(args) == 3:
            a, b, n = args
            if (valid_amount(n) and a != b and a in balances and b in balances
                    and a not in frozen and int(n) > 0 and balances[a] >= int(n)):
                amt = int(n)
                balances[a] -= amt
                balances[b] += amt
                record = ("adjust", [(a, -amt), (b, amt)])
                ok = True

        elif verb == "freeze" and len(args) == 1:
            a = args[0]
            if a in balances and a not in frozen:
                frozen.add(a)
                record = ("unfreeze", a)
                ok = True

        elif verb == "unfreeze" and len(args) == 1:
            a = args[0]
            if a in balances and a in frozen:
                frozen.discard(a)
                record = ("freeze", a)
                ok = True

        elif verb == "undo" and len(args) == 0:
            if history:
                kind, payload = history.pop()
                if kind == "delete":
                    del balances[payload]
                elif kind == "adjust":
                    for acct, delta in payload:
                        balances[acct] -= delta
                elif kind == "freeze":
                    frozen.add(payload)
                elif kind == "unfreeze":
                    frozen.discard(payload)
                ok = True

        if not ok:
            rejected.append(i)
        elif verb != "undo":
            history.append(record)

    return dict(balances), rejected
