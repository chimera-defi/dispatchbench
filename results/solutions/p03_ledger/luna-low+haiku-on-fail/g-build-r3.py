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
        success = False
        change = None

        if verb == "open" and len(tokens) == 3:
            account, raw_amount = tokens[1], tokens[2]
            if raw_amount.isascii() and raw_amount.isdigit():
                amount = int(raw_amount)
                if account not in balances:
                    balances[account] = amount
                    change = ("open", account)
                    success = True

        elif verb == "deposit" and len(tokens) == 3:
            account, raw_amount = tokens[1], tokens[2]
            if raw_amount.isascii() and raw_amount.isdigit():
                amount = int(raw_amount)
                if amount > 0 and account in balances:
                    balances[account] += amount
                    change = ("balance", account, -amount)
                    success = True

        elif verb == "withdraw" and len(tokens) == 3:
            account, raw_amount = tokens[1], tokens[2]
            if raw_amount.isascii() and raw_amount.isdigit():
                amount = int(raw_amount)
                if (amount > 0 and account in balances and account not in frozen
                        and balances[account] >= amount):
                    balances[account] -= amount
                    change = ("balance", account, amount)
                    success = True

        elif verb == "transfer" and len(tokens) == 4:
            source, target, raw_amount = tokens[1], tokens[2], tokens[3]
            if raw_amount.isascii() and raw_amount.isdigit():
                amount = int(raw_amount)
                if (amount > 0 and source != target and source in balances
                        and target in balances and source not in frozen
                        and balances[source] >= amount):
                    balances[source] -= amount
                    balances[target] += amount
                    change = ("transfer", source, target, amount)
                    success = True

        elif verb in ("freeze", "unfreeze") and len(tokens) == 2:
            account = tokens[1]
            if account in balances and ((verb == "freeze" and account not in frozen)
                                        or (verb == "unfreeze" and account in frozen)):
                was_frozen = account in frozen
                if verb == "freeze":
                    frozen.add(account)
                else:
                    frozen.remove(account)
                change = ("frozen", account, was_frozen)
                success = True

        elif verb == "undo" and len(tokens) == 1:
            if history:
                change = history.pop()
                kind = change[0]
                if kind == "open":
                    balances.pop(change[1])
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
                        frozen.discard(account)
                success = True

        if success:
            if verb != "undo":
                history.append(change)
        else:
            rejected.append(index)

    return balances, rejected
