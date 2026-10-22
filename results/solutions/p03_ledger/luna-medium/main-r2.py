def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts = {}  # name -> [balance, frozen]
    history = []
    rejected = []

    for index, operation in enumerate(ops):
        tokens = operation.split()
        if not tokens:
            rejected.append(index)
            continue

        verb = tokens[0]
        action = None

        if verb == "open":
            if len(tokens) == 3:
                name, amount_text = tokens[1], tokens[2]
                if amount_text.isdigit():
                    amount = int(amount_text)
                    if name not in accounts:
                        accounts[name] = [amount, False]
                        action = ("open", name)

        elif verb == "deposit":
            if len(tokens) == 3:
                name, amount_text = tokens[1], tokens[2]
                if amount_text.isdigit():
                    amount = int(amount_text)
                    if amount > 0 and name in accounts:
                        accounts[name][0] += amount
                        action = ("balance", name, -amount)

        elif verb == "withdraw":
            if len(tokens) == 3:
                name, amount_text = tokens[1], tokens[2]
                if amount_text.isdigit():
                    amount = int(amount_text)
                    if (amount > 0 and name in accounts
                            and not accounts[name][1]
                            and accounts[name][0] >= amount):
                        accounts[name][0] -= amount
                        action = ("balance", name, amount)

        elif verb == "transfer":
            if len(tokens) == 4:
                source, target, amount_text = tokens[1], tokens[2], tokens[3]
                if amount_text.isdigit():
                    amount = int(amount_text)
                    if (amount > 0 and source != target
                            and source in accounts and target in accounts
                            and not accounts[source][1]
                            and accounts[source][0] >= amount):
                        accounts[source][0] -= amount
                        accounts[target][0] += amount
                        action = ("transfer", source, target, amount)

        elif verb in ("freeze", "unfreeze"):
            if len(tokens) == 2:
                name = tokens[1]
                if name in accounts:
                    previous = accounts[name][1]
                    if (verb == "freeze" and not previous) or (
                        verb == "unfreeze" and previous
                    ):
                        accounts[name][1] = verb == "freeze"
                        action = ("frozen", name, previous)

        elif verb == "undo":
            if len(tokens) == 1 and history:
                action = history.pop()
                kind = action[0]

                if kind == "open":
                    del accounts[action[1]]
                elif kind == "balance":
                    _, name, delta = action
                    accounts[name][0] += delta
                elif kind == "transfer":
                    _, source, target, amount = action
                    accounts[source][0] += amount
                    accounts[target][0] -= amount
                elif kind == "frozen":
                    _, name, previous = action
                    accounts[name][1] = previous

                continue

        if action is None:
            rejected.append(index)
        else:
            history.append(action)

    return ({name: data[0] for name, data in accounts.items()}, rejected)
