def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts = {}  # name -> [balance, frozen]
    history = []
    rejected = []

    for i, operation in enumerate(ops):
        tokens = operation.split(" ")
        verb = tokens[0] if tokens else ""
        action = None

        if verb == "open" and len(tokens) == 3:
            _, name, raw = tokens
            if raw.isascii() and raw.isdigit() and name not in accounts:
                amount = int(raw)
                accounts[name] = [amount, False]
                action = ("open", name)

        elif verb == "deposit" and len(tokens) == 3:
            _, name, raw = tokens
            if raw.isascii() and raw.isdigit():
                amount = int(raw)
                if amount > 0 and name in accounts:
                    accounts[name][0] += amount
                    action = ("balance", name, -amount)

        elif verb == "withdraw" and len(tokens) == 3:
            _, name, raw = tokens
            if raw.isascii() and raw.isdigit():
                amount = int(raw)
                if (amount > 0 and name in accounts
                        and not accounts[name][1]
                        and accounts[name][0] >= amount):
                    accounts[name][0] -= amount
                    action = ("balance", name, amount)

        elif verb == "transfer" and len(tokens) == 4:
            _, source, target, raw = tokens
            if raw.isascii() and raw.isdigit():
                amount = int(raw)
                if (amount > 0 and source != target
                        and source in accounts and target in accounts
                        and not accounts[source][1]
                        and accounts[source][0] >= amount):
                    accounts[source][0] -= amount
                    accounts[target][0] += amount
                    action = ("transfer", source, target, amount)

        elif verb in ("freeze", "unfreeze") and len(tokens) == 2:
            _, name = tokens
            if name in accounts:
                was_frozen = accounts[name][1]
                if (verb == "freeze" and not was_frozen) or (
                    verb == "unfreeze" and was_frozen
                ):
                    accounts[name][1] = verb == "freeze"
                    action = ("frozen", name, was_frozen)

        elif verb == "undo" and len(tokens) == 1:
            if history:
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
            rejected.append(i)
        else:
            history.append(action)

    return ({name: state[0] for name, state in accounts.items()}, rejected)
