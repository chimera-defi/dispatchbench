def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    balances: dict[str, int] = {}
    frozen: set[str] = set()
    history: list[tuple] = []
    rejected: list[int] = []

    for index, operation in enumerate(ops):
        tokens = operation.split()
        if not tokens:
            rejected.append(index)
            continue

        verb = tokens[0]
        action = None

        if verb == "open" and len(tokens) == 3:
            name, raw_amount = tokens[1], tokens[2]
            if raw_amount.isascii() and raw_amount.isdigit():
                amount = int(raw_amount)
                if name not in balances:
                    balances[name] = amount
                    action = ("open", name)

        elif verb == "deposit" and len(tokens) == 3:
            name, raw_amount = tokens[1], tokens[2]
            if raw_amount.isascii() and raw_amount.isdigit():
                amount = int(raw_amount)
                if amount > 0 and name in balances:
                    balances[name] += amount
                    action = ("balance", name, -amount)

        elif verb == "withdraw" and len(tokens) == 3:
            name, raw_amount = tokens[1], tokens[2]
            if raw_amount.isascii() and raw_amount.isdigit():
                amount = int(raw_amount)
                if (
                    amount > 0
                    and name in balances
                    and name not in frozen
                    and balances[name] >= amount
                ):
                    balances[name] -= amount
                    action = ("balance", name, amount)

        elif verb == "transfer" and len(tokens) == 4:
            source, target, raw_amount = tokens[1], tokens[2], tokens[3]
            if raw_amount.isascii() and raw_amount.isdigit():
                amount = int(raw_amount)
                if (
                    amount > 0
                    and source != target
                    and source in balances
                    and target in balances
                    and source not in frozen
                    and balances[source] >= amount
                ):
                    balances[source] -= amount
                    balances[target] += amount
                    action = ("transfer", source, target, amount)

        elif verb == "freeze" and len(tokens) == 2:
            name = tokens[1]
            if name in balances and name not in frozen:
                frozen.add(name)
                action = ("frozen", name, False)

        elif verb == "unfreeze" and len(tokens) == 2:
            name = tokens[1]
            if name in balances and name in frozen:
                frozen.remove(name)
                action = ("frozen", name, True)

        elif verb == "undo" and len(tokens) == 1:
            if history:
                action = history.pop()
                kind = action[0]
                if kind == "open":
                    balances.pop(action[1])
                    frozen.discard(action[1])
                elif kind == "balance":
                    _, name, delta = action
                    balances[name] += delta
                elif kind == "transfer":
                    _, source, target, amount = action
                    balances[source] += amount
                    balances[target] -= amount
                elif kind == "frozen":
                    _, name, was_frozen = action
                    if was_frozen:
                        frozen.add(name)
                    else:
                        frozen.discard(name)
            else:
                rejected.append(index)
            continue

        if action is None:
            rejected.append(index)
        else:
            history.append(action)

    return balances, rejected
