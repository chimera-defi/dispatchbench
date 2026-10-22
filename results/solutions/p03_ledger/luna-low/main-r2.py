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
            name, raw_amount = tokens[1], tokens[2]
            if name in accounts or not raw_amount.isascii() or not raw_amount.isdigit():
                rejected.append(index)
                continue
            amount = int(raw_amount)
            accounts[name] = [amount, False]
            history.append(("open", name))

        elif verb == "deposit" and len(tokens) == 3:
            name, raw_amount = tokens[1], tokens[2]
            if name not in accounts or not raw_amount.isascii() or not raw_amount.isdigit():
                rejected.append(index)
                continue
            amount = int(raw_amount)
            if amount <= 0:
                rejected.append(index)
                continue
            accounts[name][0] += amount
            history.append(("deposit", name, amount))

        elif verb == "withdraw" and len(tokens) == 3:
            name, raw_amount = tokens[1], tokens[2]
            if name not in accounts or not raw_amount.isascii() or not raw_amount.isdigit():
                rejected.append(index)
                continue
            amount = int(raw_amount)
            if amount <= 0 or accounts[name][1] or accounts[name][0] < amount:
                rejected.append(index)
                continue
            accounts[name][0] -= amount
            history.append(("withdraw", name, amount))

        elif verb == "transfer" and len(tokens) == 4:
            source, target, raw_amount = tokens[1], tokens[2], tokens[3]
            if (
                source == target
                or source not in accounts
                or target not in accounts
                or not raw_amount.isascii()
                or not raw_amount.isdigit()
            ):
                rejected.append(index)
                continue
            amount = int(raw_amount)
            if amount <= 0 or accounts[source][1] or accounts[source][0] < amount:
                rejected.append(index)
                continue
            accounts[source][0] -= amount
            accounts[target][0] += amount
            history.append(("transfer", source, target, amount))

        elif verb == "freeze" and len(tokens) == 2:
            name = tokens[1]
            if name not in accounts or accounts[name][1]:
                rejected.append(index)
                continue
            accounts[name][1] = True
            history.append(("freeze", name))

        elif verb == "unfreeze" and len(tokens) == 2:
            name = tokens[1]
            if name not in accounts or not accounts[name][1]:
                rejected.append(index)
                continue
            accounts[name][1] = False
            history.append(("unfreeze", name))

        else:
            rejected.append(index)

    return ({name: state[0] for name, state in accounts.items()}, rejected)
