def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    balances: dict[str, int] = {}
    frozen: dict[str, bool] = {}
    history: list[tuple] = []
    rejected: list[int] = []

    def parse_amount(token: str) -> int | None:
        if not token or any(ch < "0" or ch > "9" for ch in token):
            return None
        value = 0
        for ch in token:
            value = value * 10 + ord(ch) - ord("0")
        return value

    for i, operation in enumerate(ops):
        parts = operation.split()
        verb = parts[0] if parts else ""
        success = False

        if verb == "open" and len(parts) == 3:
            account = parts[1]
            amount = parse_amount(parts[2])
            if amount is not None and account not in balances:
                balances[account] = amount
                frozen[account] = False
                history.append(("open", account))
                success = True

        elif verb == "deposit" and len(parts) == 3:
            account = parts[1]
            amount = parse_amount(parts[2])
            if amount is not None and amount > 0 and account in balances:
                balances[account] += amount
                history.append(("deposit", account, amount))
                success = True

        elif verb == "withdraw" and len(parts) == 3:
            account = parts[1]
            amount = parse_amount(parts[2])
            if (
                amount is not None
                and amount > 0
                and account in balances
                and not frozen[account]
                and balances[account] >= amount
            ):
                balances[account] -= amount
                history.append(("withdraw", account, amount))
                success = True

        elif verb == "transfer" and len(parts) == 4:
            source, destination = parts[1], parts[2]
            amount = parse_amount(parts[3])
            if (
                amount is not None
                and amount > 0
                and source != destination
                and source in balances
                and destination in balances
                and not frozen[source]
                and balances[source] >= amount
            ):
                balances[source] -= amount
                balances[destination] += amount
                history.append(("transfer", source, destination, amount))
                success = True

        elif verb == "freeze" and len(parts) == 2:
            account = parts[1]
            if account in balances and not frozen[account]:
                frozen[account] = True
                history.append(("freeze", account, False))
                success = True

        elif verb == "unfreeze" and len(parts) == 2:
            account = parts[1]
            if account in balances and frozen[account]:
                frozen[account] = False
                history.append(("unfreeze", account, True))
                success = True

        elif verb == "undo" and len(parts) == 1:
            if history:
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
                    _, source, destination, amount = action
                    balances[source] += amount
                    balances[destination] -= amount
                else:
                    _, account, previous_state = action
                    frozen[account] = previous_state

                success = True

        if not success:
            rejected.append(i)

    return balances, rejected
