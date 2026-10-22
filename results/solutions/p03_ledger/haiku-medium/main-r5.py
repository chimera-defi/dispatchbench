def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    digits = "0123456789"
    accounts: dict[str, list] = {}  # name -> [balance, frozen]
    history: list[list[tuple[str, list | None]]] = []  # undo records
    rejected: list[int] = []

    def parse_amount(tok: str) -> int | None:
        if not tok or any(c not in digits for c in tok):
            return None
        return int(tok)

    def snap(*names: str) -> list[tuple[str, list | None]]:
        return [(nm, list(accounts[nm]) if nm in accounts else None) for nm in names]

    for i, op in enumerate(ops):
        parts = op.split(" ")
        verb = parts[0]
        n = len(parts)
        ok = False
        record = None

        if verb == "open" and n == 3:
            name = parts[1]
            amt = parse_amount(parts[2])
            if amt is not None and name not in accounts:
                record = snap(name)
                accounts[name] = [amt, False]
                ok = True

        elif verb == "deposit" and n == 3:
            name = parts[1]
            amt = parse_amount(parts[2])
            if amt is not None and amt > 0 and name in accounts:
                record = snap(name)
                accounts[name][0] += amt
                ok = True

        elif verb == "withdraw" and n == 3:
            name = parts[1]
            amt = parse_amount(parts[2])
            if (amt is not None and amt > 0 and name in accounts
                    and not accounts[name][1] and accounts[name][0] >= amt):
                record = snap(name)
                accounts[name][0] -= amt
                ok = True

        elif verb == "transfer" and n == 4:
            src, dst = parts[1], parts[2]
            amt = parse_amount(parts[3])
            if (amt is not None and amt > 0 and src != dst
                    and src in accounts and dst in accounts
                    and not accounts[src][1] and accounts[src][0] >= amt):
                record = snap(src, dst)
                accounts[src][0] -= amt
                accounts[dst][0] += amt
                ok = True

        elif verb == "freeze" and n == 2:
            name = parts[1]
            if name in accounts and not accounts[name][1]:
                record = snap(name)
                accounts[name][1] = True
                ok = True

        elif verb == "unfreeze" and n == 2:
            name = parts[1]
            if name in accounts and accounts[name][1]:
                record = snap(name)
                accounts[name][1] = False
                ok = True

        elif verb == "undo" and n == 1:
            if history:
                for nm, st in history.pop():
                    if st is None:
                        accounts.pop(nm, None)
                    else:
                        accounts[nm] = st
                ok = True
            # undo operations are never recorded, so they cannot be reverted

        if not ok:
            rejected.append(i)
        elif record is not None:
            history.append(record)

    balances = {name: vals[0] for name, vals in accounts.items()}
    return balances, rejected
