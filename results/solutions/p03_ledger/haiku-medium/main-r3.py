def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    digits = set("0123456789")

    def parse_amount(tok: str):
        if not tok or any(c not in digits for c in tok):
            return None
        return int(tok)

    balances: dict[str, int] = {}
    frozen: dict[str, bool] = {}
    # Each entry is a compensating action for one successful, non-undo operation.
    history: list[tuple] = []
    rejected: list[int] = []

    for i, op in enumerate(ops):
        parts = op.split(" ")
        verb = parts[0]
        ok = False

        if verb == "open" and len(parts) == 3:
            name, amt = parts[1], parse_amount(parts[2])
            if amt is not None and name not in balances:
                balances[name] = amt
                frozen[name] = False
                history.append(("remove", name))
                ok = True

        elif verb == "deposit" and len(parts) == 3:
            name, amt = parts[1], parse_amount(parts[2])
            if amt is not None and amt > 0 and name in balances:
                balances[name] += amt
                history.append(("add", name, -amt))
                ok = True

        elif verb == "withdraw" and len(parts) == 3:
            name, amt = parts[1], parse_amount(parts[2])
            if (amt is not None and amt > 0 and name in balances
                    and not frozen[name] and balances[name] >= amt):
                balances[name] -= amt
                history.append(("add", name, amt))
                ok = True

        elif verb == "transfer" and len(parts) == 4:
            src, dst, amt = parts[1], parts[2], parse_amount(parts[3])
            if (amt is not None and amt > 0 and src != dst
                    and src in balances and dst in balances
                    and not frozen[src] and balances[src] >= amt):
                balances[src] -= amt
                balances[dst] += amt
                history.append(("transfer", src, dst, amt))
                ok = True

        elif verb == "freeze" and len(parts) == 2:
            name = parts[1]
            if name in balances and not frozen[name]:
                frozen[name] = True
                history.append(("frozen", name, False))
                ok = True

        elif verb == "unfreeze" and len(parts) == 2:
            name = parts[1]
            if name in balances and frozen[name]:
                frozen[name] = False
                history.append(("frozen", name, True))
                ok = True

        elif verb == "undo" and len(parts) == 1:
            if history:
                action = history.pop()
                kind = action[0]
                if kind == "remove":
                    name = action[1]
                    del balances[name]
                    del frozen[name]
                elif kind == "add":
                    balances[action[1]] += action[2]
                elif kind == "transfer":
                    _, src, dst, amt = action
                    balances[src] += amt
                    balances[dst] -= amt
                elif kind == "frozen":
                    frozen[action[1]] = action[2]
                ok = True

        if not ok:
            rejected.append(i)

    return dict(balances), rejected
