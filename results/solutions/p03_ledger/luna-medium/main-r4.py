def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    balances: dict[str, int] = {}
    frozen: set[str] = set()
    history = []
    rejected = []

    for index, operation in enumerate(ops):
        tokens = operation.split(" ")
        verb = tokens[0] if tokens else ""

        if verb == "undo" and len(tokens) == 1:
            if not history:
                rejected.append(index)
                continue

            kind, data = history.pop()
            if kind == "open":
                balances.pop(data, None)
                frozen.discard(data)
            elif kind == "balance":
                account, old_balance = data
                balances[account] = old_balance
            elif kind == "freeze":
                account, was_frozen = data
                if was_frozen:
                    frozen.add(account)
                else:
                    frozen.discard(account)
            continue

        if verb == "open" and len(tokens) == 3:
            account, amount = tokens[1], tokens[2]
            if (account in balances or not amount.isdigit()
                    or not amount.isascii()):
                rejected.append(index)
                continue
            balances[account] = int(amount)
            history.append(("open", account))
            continue

        if verb in ("deposit", "withdraw") and len(tokens) == 3:
            account, amount = tokens[1], tokens[2]
            if (not amount.isdigit() or not amount.isascii()
                    or int(amount) <= 0 or account not in balances):
                rejected.append(index)
                continue
            value = int(amount)
            if verb == "withdraw" and (
                account in frozen or balances[account] < value
            ):
                rejected.append(index)
                continue
            history.append(("balance", (account, balances[account])))
            balances[account] += value if verb == "deposit" else -value
            continue

        if verb == "transfer" and len(tokens) == 4:
            source, destination, amount = tokens[1], tokens[2], tokens[3]
            if (not amount.isdigit() or not amount.isascii()
                    or int(amount) <= 0 or source == destination
                    or source not in balances or destination not in balances
                    or source in frozen or balances[source] < int(amount)):
                rejected.append(index)
                continue
            value = int(amount)
            history.append(("balance", (
                source, balances[source], destination, balances[destination]
            )))
            balances[source] -= value
            balances[destination] += value
            continue

        if verb in ("freeze", "unfreeze") and len(tokens) == 2:
            account = tokens[1]
            is_frozen = account in frozen
            if account not in balances or (verb == "freeze" and is_frozen) or (
                verb == "unfreeze" and not is_frozen
            ):
                rejected.append(index)
                continue
            history.append(("freeze", (account, is_frozen)))
            if verb == "freeze":
                frozen.add(account)
            else:
                frozen.remove(account)
            continue

        rejected.append(index)

    return balances, rejected
