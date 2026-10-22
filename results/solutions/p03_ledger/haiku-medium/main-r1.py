def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts: dict[str, list] = {}  # name -> [balance, frozen]
    history: list[tuple] = []  # inverse records for successful non-undo ops
    rejected: list[int] = []

    def parse_amount(s: str):
        if s == "" or any(c not in "0123456789" for c in s):
            return None
        return int(s)

    for i, op in enumerate(ops):
        tokens = op.split(" ")
        verb = tokens[0]
        success = False

        if verb == "open" and len(tokens) == 3:
            name = tokens[1]
            amt = parse_amount(tokens[2])
            if amt is not None and name not in accounts:
                accounts[name] = [amt, False]
                history.append(("open", name))
                success = True

        elif verb == "deposit" and len(tokens) == 3:
            name = tokens[1]
            amt = parse_amount(tokens[2])
            if amt is not None and amt > 0 and name in accounts:
                accounts[name][0] += amt
                history.append(("deposit", name, amt))
                success = True

        elif verb == "withdraw" and len(tokens) == 3:
            name = tokens[1]
            amt = parse_amount(tokens[2])
            if (
                amt is not None
                and amt > 0
                and name in accounts
                and not accounts[name][1]
                and accounts[name][0] >= amt
            ):
                accounts[name][0] -= amt
                history.append(("withdraw", name, amt))
                success = True

        elif verb == "transfer" and len(tokens) == 4:
            src, dst = tokens[1], tokens[2]
            amt = parse_amount(tokens[3])
            if (
                amt is not None
                and amt > 0
                and src != dst
                and src in accounts
                and dst in accounts
                and not accounts[src][1]
                and accounts[src][0] >= amt
            ):
                accounts[src][0] -= amt
                accounts[dst][0] += amt
                history.append(("transfer", src, dst, amt))
                success = True

        elif verb == "freeze" and len(tokens) == 2:
            name = tokens[1]
            if name in accounts and not accounts[name][1]:
                accounts[name][1] = True
                history.append(("freeze", name))
                success = True

        elif verb == "unfreeze" and len(tokens) == 2:
            name = tokens[1]
            if name in accounts and accounts[name][1]:
                accounts[name][1] = False
                history.append(("unfreeze", name))
                success = True

        elif verb == "undo" and len(tokens) == 1:
            if history:
                rec = history.pop()  # undo records are never pushed, so undo cannot be undone
                kind = rec[0]
                if kind == "open":
                    del accounts[rec[1]]
                elif kind == "deposit":
                    accounts[rec[1]][0] -= rec[2]
                elif kind == "withdraw":
                    accounts[rec[1]][0] += rec[2]
                elif kind == "transfer":
                    accounts[rec[1]][0] += rec[3]
                    accounts[rec[2]][0] -= rec[3]
                elif kind == "freeze":
                    accounts[rec[1]][1] = False
                elif kind == "unfreeze":
                    accounts[rec[1]][1] = True
                success = True

        if not success:
            rejected.append(i)

    balances = {name: data[0] for name, data in accounts.items()}
    return balances, rejected
