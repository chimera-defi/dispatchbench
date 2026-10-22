def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts = {}  # name -> [balance, frozen]
    history = []
    rejected = []

    for index, operation in enumerate(ops):
        tokens = operation.split(" ")
        verb = tokens[0] if tokens else ""

        if verb == "undo":
            if len(tokens) != 1 or not history:
                rejected.append(index)
                continue

            action = history.pop()
            kind = action[0]

            if kind == "open":
                del accounts[action[1]]
            elif kind == "deposit":
                accounts[action[1]][0] -= action[2]
            elif kind == "withdraw":
                accounts[action[1]][0] += action[2]
            elif kind == "transfer":
                accounts[action[1]][0] += action[3]
                accounts[action[2]][0] -= action[3]
            elif kind == "freeze":
                accounts[action[1]][1] = False
            elif kind == "unfreeze":
                accounts[action[1]][1] = True
            continue

        if verb == "open" and len(tokens) == 3:
            name, amount = tokens[1], tokens[2]
            if name not in accounts and amount.isascii() and amount.isdigit():
                value = int(amount)
                accounts[name] = [value, False]
                history.append(("open", name))
                continue

        elif verb == "deposit" and len(tokens) == 3:
            name, amount = tokens[1], tokens[2]
            if amount.isascii() and amount.isdigit():
                value = int(amount)
                if value > 0 and name in accounts:
                    accounts[name][0] += value
                    history.append(("deposit", name, value))
                    continue

        elif verb == "withdraw" and len(tokens) == 3:
            name, amount = tokens[1], tokens[2]
            if amount.isascii() and amount.isdigit():
                value = int(amount)
                if (value > 0 and name in accounts
                        and not accounts[name][1]
                        and accounts[name][0] >= value):
                    accounts[name][0] -= value
                    history.append(("withdraw", name, value))
                    continue

        elif verb == "transfer" and len(tokens) == 4:
            source, target, amount = tokens[1], tokens[2], tokens[3]
            if amount.isascii() and amount.isdigit():
                value = int(amount)
                if (value > 0 and source != target
                        and source in accounts and target in accounts
                        and not accounts[source][1]
                        and accounts[source][0] >= value):
                    accounts[source][0] -= value
                    accounts[target][0] += value
                    history.append(("transfer", source, target, value))
                    continue

        elif verb == "freeze" and len(tokens) == 2:
            name = tokens[1]
            if name in accounts and not accounts[name][1]:
                accounts[name][1] = True
                history.append(("freeze", name))
                continue

        elif verb == "unfreeze" and len(tokens) == 2:
            name = tokens[1]
            if name in accounts and accounts[name][1]:
                accounts[name][1] = False
                history.append(("unfreeze", name))
                continue

        rejected.append(index)

    return {name: state[0] for name, state in accounts.items()}, rejected
