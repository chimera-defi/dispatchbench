def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts = {}
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
            elif kind == "balance":
                accounts[action[1]][0] = action[2]
                if action[3]:
                    accounts[action[4]][0] = action[5]
            elif kind == "frozen":
                accounts[action[1]][1] = action[2]
            continue

        if verb == "open":
            if len(tokens) != 3:
                rejected.append(index)
                continue
            _, name, amount = tokens
            if not amount.isascii() or not amount.isdigit() or name in accounts:
                rejected.append(index)
                continue
            value = int(amount)
            accounts[name] = [value, False]
            history.append(("open", name))

        elif verb == "deposit":
            if len(tokens) != 3:
                rejected.append(index)
                continue
            _, name, amount = tokens
            if not amount.isascii() or not amount.isdigit():
                rejected.append(index)
                continue
            value = int(amount)
            if value <= 0 or name not in accounts:
                rejected.append(index)
                continue
            old = accounts[name][0]
            accounts[name][0] += value
            history.append(("balance", name, old, False, None, None))

        elif verb == "withdraw":
            if len(tokens) != 3:
                rejected.append(index)
                continue
            _, name, amount = tokens
            if not amount.isascii() or not amount.isdigit():
                rejected.append(index)
                continue
            value = int(amount)
            if (value <= 0 or name not in accounts or accounts[name][1]
                    or accounts[name][0] < value):
                rejected.append(index)
                continue
            old = accounts[name][0]
            accounts[name][0] -= value
            history.append(("balance", name, old, False, None, None))

        elif verb == "transfer":
            if len(tokens) != 4:
                rejected.append(index)
                continue
            _, source, target, amount = tokens
            if not amount.isascii() or not amount.isdigit():
                rejected.append(index)
                continue
            value = int(amount)
            if (value <= 0 or source == target or source not in accounts
                    or target not in accounts or accounts[source][1]
                    or accounts[source][0] < value):
                rejected.append(index)
                continue
            old_source = accounts[source][0]
            old_target = accounts[target][0]
            accounts[source][0] -= value
            accounts[target][0] += value
            history.append(("balance", source, old_source, True, target, old_target))

        elif verb == "freeze":
            if len(tokens) != 2:
                rejected.append(index)
                continue
            _, name = tokens
            if name not in accounts or accounts[name][1]:
                rejected.append(index)
                continue
            accounts[name][1] = True
            history.append(("frozen", name, False))

        elif verb == "unfreeze":
            if len(tokens) != 2:
                rejected.append(index)
                continue
            _, name = tokens
            if name not in accounts or not accounts[name][1]:
                rejected.append(index)
                continue
            accounts[name][1] = False
            history.append(("frozen", name, True))

        else:
            rejected.append(index)

    return {name: state[0] for name, state in accounts.items()}, rejected
