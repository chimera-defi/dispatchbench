def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts: dict[str, dict] = {}  # name -> {"balance": int, "frozen": bool}
    history: list = []  # stack of (undo_fn_data) for successful non-undo ops
    rejected: list[int] = []

    def valid_amount(tok: str):
        if not tok or not all("0" <= c <= "9" for c in tok):
            return None
        return int(tok)

    def snapshot():
        return {k: dict(v) for k, v in accounts.items()}

    for idx, op in enumerate(ops):
        tokens = op.split(" ")
        verb = tokens[0] if tokens else ""
        ok = False
        entry = None

        if verb == "undo":
            if len(tokens) != 1 or not history:
                rejected.append(idx)
                continue
            kind, data = history.pop()
            if kind == "open":
                del accounts[data]
            elif kind == "restore":
                accounts.clear()
                accounts.update(data)
            elif kind == "snapshot":
                accounts.clear()
                accounts.update(data)
            continue

        if verb == "open" and len(tokens) == 3:
            name, amt = tokens[1], valid_amount(tokens[2])
            if amt is not None and name not in accounts:
                accounts[name] = {"balance": amt, "frozen": False}
                entry = ("open", name)
                ok = True

        elif verb == "deposit" and len(tokens) == 3:
            name, amt = tokens[1], valid_amount(tokens[2])
            if amt is not None and amt > 0 and name in accounts:
                entry = ("restore", snapshot())
                accounts[name]["balance"] += amt
                ok = True

        elif verb == "withdraw" and len(tokens) == 3:
            name, amt = tokens[1], valid_amount(tokens[2])
            if (amt is not None and amt > 0 and name in accounts
                    and not accounts[name]["frozen"]
                    and accounts[name]["balance"] >= amt):
                entry = ("restore", snapshot())
                accounts[name]["balance"] -= amt
                ok = True

        elif verb == "transfer" and len(tokens) == 4:
            a, b, amt = tokens[1], tokens[2], valid_amount(tokens[3])
            if (amt is not None and amt > 0 and a != b
                    and a in accounts and b in accounts
                    and not accounts[a]["frozen"]
                    and accounts[a]["balance"] >= amt):
                entry = ("restore", snapshot())
                accounts[a]["balance"] -= amt
                accounts[b]["balance"] += amt
                ok = True

        elif verb == "freeze" and len(tokens) == 2:
            name = tokens[1]
            if name in accounts and not accounts[name]["frozen"]:
                entry = ("restore", snapshot())
                accounts[name]["frozen"] = True
                ok = True

        elif verb == "unfreeze" and len(tokens) == 2:
            name = tokens[1]
            if name in accounts and accounts[name]["frozen"]:
                entry = ("restore", snapshot())
                accounts[name]["frozen"] = False
                ok = True

        if ok:
            history.append(entry)
        else:
            rejected.append(idx)

    balances = {k: v["balance"] for k, v in accounts.items()}
    return balances, rejected
