def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    balances: dict[str, int] = {}
    frozen: set[str] = set()
    history: list[tuple] = []
    rejected: list[int] = []

    def valid_amount(token: str) -> bool:
        return bool(token) and all("0" <= ch <= "9" for ch in token)

    for i, operation in enumerate(ops):
        parts = operation.split()
        if not parts:
            rejected.append(i)
            continue

        verb = parts[0]
        success = False

        if verb == "open" and len(parts) == 3:
            _, account, amount = parts
            if valid_amount(amount) and account not in balances:
                balances[account] = int(amount)
                history.append(("open", account))
                success = True

        elif verb == "deposit" and len(parts) == 3:
            _, account, amount = parts
            if valid_amount(amount) and int(amount) > 0 and account in balances:
                value = int(amount)
                balances[account] += value
                history.append(("deposit", account, value))
                success = True

        elif verb == "withdraw" and len(parts) == 3:
            _, account, amount = parts
            if valid_amount(amount) and int(amount) > 0 and account in balances and account not in frozen:
                value = int(amount)
                if balances[account] >= value:
                    balances[account] -= value
                    history.append(("withdraw", account, value))
                    success = True

        elif verb == "transfer" and len(parts) == 4:
            _, source, destination, amount = parts
            if (
                valid_amount(amount)
                and int(amount) > 0
                and source != destination
                and source in balances
                and destination in balances
                and source not in frozen
            ):
                value = int(amount)
                if balances[source] >= value:
                    balances[source] -= value
                    balances[destination] += value
                    history.append(("transfer", source, destination, value))
                    success = True

        elif verb == "freeze" and len(parts) == 2:
            account = parts[1]
            if account in balances and account not in frozen:
                frozen.add(account)
                history.append(("state", account, False))
                success = True

        elif verb == "unfreeze" and len(parts) == 2:
            account = parts[1]
            if account in balances and account in frozen:
                frozen.remove(account)
                history.append(("state", account, True))
                success = True

        elif verb == "undo" and len(parts) == 1:
            if history:
                action = history.pop()
                kind = action[0]

                if kind == "open":
                    account = action[1]
                    del balances[account]
                    frozen.discard(account)
                elif kind == "deposit":
                    _, account, value = action
                    balances[account] -= value
                elif kind == "withdraw":
                    _, account, value = action
                    balances[account] += value
                elif kind == "transfer":
                    _, source, destination, value = action
                    balances[source] += value
                    balances[destination] -= value
                else:
                    _, account, was_frozen = action
                    if was_frozen:
                        frozen.add(account)
                    else:
                        frozen.discard(account)
                success = True

        if not success:
            rejected.append(i)

    return balances, rejected
