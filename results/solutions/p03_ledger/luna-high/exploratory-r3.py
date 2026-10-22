def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    balances: dict[str, int] = {}
    frozen: dict[str, bool] = {}
    history: list[tuple] = []
    rejected: list[int] = []

    def valid_amount(token: str) -> bool:
        return bool(token) and all("0" <= ch <= "9" for ch in token)

    for i, operation in enumerate(ops):
        tokens = operation.split()
        if not tokens:
            rejected.append(i)
            continue

        verb = tokens[0]

        if verb == "undo":
            if len(tokens) != 1 or not history:
                rejected.append(i)
                continue

            action = history.pop()
            kind = action[0]

            if kind == "open":
                account = action[1]
                del balances[account]
                del frozen[account]
            elif kind == "deposit":
                _, account, amount = action
                balances[account] -= amount
            elif kind == "withdraw":
                _, account, amount = action
                balances[account] += amount
            elif kind == "transfer":
                _, source, target, amount = action
                balances[source] += amount
                balances[target] -= amount
            elif kind == "freeze":
                _, account, previous = action
                frozen[account] = previous

        elif verb == "open":
            if len(tokens) != 3 or not valid_amount(tokens[2]) or tokens[1] in balances:
                rejected.append(i)
                continue
            account, amount = tokens[1], int(tokens[2])
            balances[account] = amount
            frozen[account] = False
            history.append(("open", account))

        elif verb == "deposit":
            if len(tokens) != 3 or not valid_amount(tokens[2]):
                rejected.append(i)
                continue
            account, amount = tokens[1], int(tokens[2])
            if amount <= 0 or account not in balances:
                rejected.append(i)
                continue
            balances[account] += amount
            history.append(("deposit", account, amount))

        elif verb == "withdraw":
            if len(tokens) != 3 or not valid_amount(tokens[2]):
                rejected.append(i)
                continue
            account, amount = tokens[1], int(tokens[2])
            if amount <= 0 or account not in balances or frozen[account] or balances[account] < amount:
                rejected.append(i)
                continue
            balances[account] -= amount
            history.append(("withdraw", account, amount))

        elif verb == "transfer":
            if len(tokens) != 4 or not valid_amount(tokens[3]):
                rejected.append(i)
                continue
            source, target, amount = tokens[1], tokens[2], int(tokens[3])
            if (
                amount <= 0
                or source == target
                or source not in balances
                or target not in balances
                or frozen[source]
                or balances[source] < amount
            ):
                rejected.append(i)
                continue
            balances[source] -= amount
            balances[target] += amount
            history.append(("transfer", source, target, amount))

        elif verb == "freeze":
            if len(tokens) != 2:
                rejected.append(i)
                continue
            account = tokens[1]
            if account not in balances or frozen[account]:
                rejected.append(i)
                continue
            history.append(("freeze", account, frozen[account]))
            frozen[account] = True

        elif verb == "unfreeze":
            if len(tokens) != 2:
                rejected.append(i)
                continue
            account = tokens[1]
            if account not in balances or not frozen[account]:
                rejected.append(i)
                continue
            history.append(("freeze", account, frozen[account]))
            frozen[account] = False

        else:
            rejected.append(i)

    return balances, rejected
