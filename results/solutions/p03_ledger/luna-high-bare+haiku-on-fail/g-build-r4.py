def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    balances: dict[str, int] = {}
    frozen: dict[str, bool] = {}
    history: list[tuple] = []
    rejected: list[int] = []

    def parse_amount(token: str) -> int | None:
        if not token or any(ch < "0" or ch > "9" for ch in token):
            return None
        return int(token)

    for i, operation in enumerate(ops):
        tokens = operation.split(" ")
        verb = tokens[0]

        if verb == "undo" and len(tokens) == 1:
            if not history:
                rejected.append(i)
                continue

            record = history.pop()
            kind = record[0]

            if kind == "open":
                _, account = record
                del balances[account]
                del frozen[account]
            elif kind == "deposit":
                _, account, amount = record
                balances[account] -= amount
            elif kind == "withdraw":
                _, account, amount = record
                balances[account] += amount
            elif kind == "transfer":
                _, source, destination, amount = record
                balances[source] += amount
                balances[destination] -= amount
            elif kind == "freeze":
                _, account, previous = record
                frozen[account] = previous
            continue

        if verb == "open" and len(tokens) == 3:
            account = tokens[1]
            amount = parse_amount(tokens[2])
            if amount is None or account in balances:
                rejected.append(i)
                continue
            balances[account] = amount
            frozen[account] = False
            history.append(("open", account))

        elif verb == "deposit" and len(tokens) == 3:
            account = tokens[1]
            amount = parse_amount(tokens[2])
            if amount is None or amount <= 0 or account not in balances:
                rejected.append(i)
                continue
            balances[account] += amount
            history.append(("deposit", account, amount))

        elif verb == "withdraw" and len(tokens) == 3:
            account = tokens[1]
            amount = parse_amount(tokens[2])
            if (amount is None or amount <= 0 or account not in balances
                    or frozen[account] or balances[account] < amount):
                rejected.append(i)
                continue
            balances[account] -= amount
            history.append(("withdraw", account, amount))

        elif verb == "transfer" and len(tokens) == 4:
            source, destination = tokens[1], tokens[2]
            amount = parse_amount(tokens[3])
            if (amount is None or amount <= 0 or source == destination
                    or source not in balances or destination not in balances
                    or frozen[source] or balances[source] < amount):
                rejected.append(i)
                continue
            balances[source] -= amount
            balances[destination] += amount
            history.append(("transfer", source, destination, amount))

        elif verb in ("freeze", "unfreeze") and len(tokens) == 2:
            account = tokens[1]
            if account not in balances:
                rejected.append(i)
                continue
            previous = frozen[account]
            if (verb == "freeze" and previous) or (verb == "unfreeze" and not previous):
                rejected.append(i)
                continue
            frozen[account] = verb == "freeze"
            history.append(("freeze", account, previous))

        else:
            rejected.append(i)

    return balances, rejected
