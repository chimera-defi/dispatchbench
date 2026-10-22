def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts: dict[str, list] = {}  # name -> [balance, frozen]
    history: list[list[tuple]] = []  # inverse actions for each successful non-undo op
    rejected: list[int] = []

    def parse(s: str):
        if not s or any(c not in "0123456789" for c in s):
            return None
        return int(s)

    for i, op in enumerate(ops):
        t = op.split(" ")
        verb = t[0]
        rec = None  # inverse actions; None means nothing to record
        ok = False

        if verb == "open" and len(t) == 3:
            name, n = t[1], parse(t[2])
            if n is not None and name not in accounts:
                accounts[name] = [n, False]
                rec = [("del", name)]
                ok = True

        elif verb == "deposit" and len(t) == 3:
            name, n = t[1], parse(t[2])
            if n is not None and n > 0 and name in accounts:
                accounts[name][0] += n
                rec = [("bal", name, -n)]
                ok = True

        elif verb == "withdraw" and len(t) == 3:
            name, n = t[1], parse(t[2])
            if (n is not None and n > 0 and name in accounts
                    and not accounts[name][1] and accounts[name][0] >= n):
                accounts[name][0] -= n
                rec = [("bal", name, n)]
                ok = True

        elif verb == "transfer" and len(t) == 4:
            a, b, n = t[1], t[2], parse(t[3])
            if (n is not None and n > 0 and a != b
                    and a in accounts and b in accounts
                    and not accounts[a][1] and accounts[a][0] >= n):
                accounts[a][0] -= n
                accounts[b][0] += n
                rec = [("bal", a, n), ("bal", b, -n)]
                ok = True

        elif verb == "freeze" and len(t) == 2:
            name = t[1]
            if name in accounts and not accounts[name][1]:
                accounts[name][1] = True
                rec = [("frz", name, False)]
                ok = True

        elif verb == "unfreeze" and len(t) == 2:
            name = t[1]
            if name in accounts and accounts[name][1]:
                accounts[name][1] = False
                rec = [("frz", name, True)]
                ok = True

        elif verb == "undo" and len(t) == 1:
            if history:
                for action in reversed(history.pop()):
                    if action[0] == "del":
                        del accounts[action[1]]
                    elif action[0] == "bal":
                        accounts[action[1]][0] += action[2]
                    elif action[0] == "frz":
                        accounts[action[1]][1] = action[2]
                ok = True
            # undo operations are never pushed onto history

        if ok:
            if verb != "undo":
                history.append(rec)
        else:
            rejected.append(i)

    balances = {name: acc[0] for name, acc in accounts.items()}
    return balances, rejected
