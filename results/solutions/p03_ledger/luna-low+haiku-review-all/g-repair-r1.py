def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    balances: dict[str, int] = {}
    frozen: set[str] = set()
    history: list[tuple] = []
    rejected: list[int] = []

    def valid_amount(token: str) -> bool:
        return bool(token) and all("0" <= ch <= "9" for ch in token)

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
                _, account = action
                del balances[account]
                frozen.discard(account)
            elif kind == "balance":
                _, account, delta = action
                balances[account] -= delta
            elif kind == "transfer":
                _, source, destination, amount = action
                balances[source] += amount
                balances[destination] -= amount
            elif kind == "freeze":
                _, account, was_frozen = action
                if was_frozen:
                    frozen.add(account)
                else:
                    frozen.discard(account)
            continue

        if verb == "open":
            if len(tokens) != 3 or not valid_amount(tokens[2]):
                rejected.append(index)
                continue
            account, amount = tokens[1], int(tokens[2])
            if account in balances:
                rejected.append(index)
                continue
            balances[account] = amount
            history.append(("open", account))

        elif verb == "deposit":
            if len(tokens) != 3 or not valid_amount(tokens[2]):
                rejected.append(index)
                continue
            account, amount = tokens[1], int(tokens[2])
            if amount <= 0 or account not in balances:
                rejected.append(index)
                continue
            balances[account] += amount
            history.append(("balance", account, amount))

        elif verb == "withdraw":
            if len(tokens) != 3 or not valid_amount(tokens[2]):
                rejected.append(index)
                continue
            account, amount = tokens[1], int(tokens[2])
            if (
                amount <= 0
                or account not in balances
                or account in frozen
                or balances[account] < amount
            ):
                rejected.append(index)
                continue
            balances[account] -= amount
            history.append(("balance", account, -amount))

        elif verb == "transfer":
            if len(tokens) != 4 or not valid_amount(tokens[3]):
                rejected.append(index)
                continue
            source, destination, amount = tokens[1], tokens[2], int(tokens[3])
            if (
                amount <= 0
                or source == destination
                or source not in balances
                or destination not in balances
                or source in frozen
                or balances[source] < amount
            ):
                rejected.append(index)
                continue
            balances[source] -= amount
            balances[destination] += amount
            history.append(("transfer", source, destination, amount))

        elif verb == "freeze":
            if len(tokens) != 2:
                rejected.append(index)
                continue
            account = tokens[1]
            if account not in balances or account in frozen:
                rejected.append(index)
                continue
            frozen.add(account)
            history.append(("freeze", account, False))

        elif verb == "unfreeze":
            if len(tokens) != 2:
                rejected.append(index)
                continue
            account = tokens[1]
            if account not in balances or account not in frozen:
                rejected.append(index)
                continue
            frozen.remove(account)
            history.append(("freeze", account, True))

        else:
            rejected.append(index)

    return balances, rejected
