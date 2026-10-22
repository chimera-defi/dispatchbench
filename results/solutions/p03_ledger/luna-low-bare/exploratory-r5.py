def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    balances = {}
    frozen = set()
    history = []
    rejected = []

    for index, operation in enumerate(ops):
        tokens = operation.split()
        if not tokens:
            rejected.append(index)
            continue

        verb = tokens[0]
        change = None

        if verb == "open" and len(tokens) == 3:
            account, amount_text = tokens[1], tokens[2]
            if amount_text.isascii() and amount_text.isdigit():
                amount = int(amount_text)
                if account not in balances:
                    balances[account] = amount
                    change = ("open", account, amount)

        elif verb == "deposit" and len(tokens) == 3:
            account, amount_text = tokens[1], tokens[2]
            if amount_text.isascii() and amount_text.isdigit():
                amount = int(amount_text)
                if amount > 0 and account in balances:
                    balances[account] += amount
                    change = ("balance", account, -amount)

        elif verb == "withdraw" and len(tokens) == 3:
            account, amount_text = tokens[1], tokens[2]
            if amount_text.isascii() and amount_text.isdigit():
                amount = int(amount_text)
                if (amount > 0 and account in balances and account not in frozen
                        and balances[account] >= amount):
                    balances[account] -= amount
                    change = ("balance", account, amount)

        elif verb == "transfer" and len(tokens) == 4:
            source, target, amount_text = tokens[1], tokens[2], tokens[3]
            if amount_text.isascii() and amount_text.isdigit():
                amount = int(amount_text)
                if (amount > 0 and source != target and source in balances
                        and target in balances and source not in frozen
                        and balances[source] >= amount):
                    balances[source] -= amount
                    balances[target] += amount
                    change = ("transfer", source, target, amount)

        elif verb in ("freeze", "unfreeze") and len(tokens) == 2:
            account = tokens[1]
            if account in balances:
                if verb == "freeze" and account not in frozen:
                    frozen.add(account)
                    change = ("frozen", account, False)
                elif verb == "unfreeze" and account in frozen:
                    frozen.remove(account)
                    change = ("frozen", account, True)

        elif verb == "undo" and len(tokens) == 1:
            if history:
                change = history.pop()
                kind = change[0]
                if kind == "open":
                    del balances[change[1]]
                    frozen.discard(change[1])
                elif kind == "balance":
                    _, account, delta = change
                    balances[account] += delta
                elif kind == "transfer":
                    _, source, target, amount = change
                    balances[source] += amount
                    balances[target] -= amount
                elif kind == "frozen":
                    _, account, was_frozen = change
                    if was_frozen:
                        frozen.add(account)
                    else:
                        frozen.remove(account)
                continue

        if change is None:
            rejected.append(index)
        else:
            history.append(change)

    return balances, rejected
