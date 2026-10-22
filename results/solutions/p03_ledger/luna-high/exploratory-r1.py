def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    balances: dict[str, int] = {}
    frozen: set[str] = set()
    history: list[tuple] = []
    rejected: list[int] = []

    def valid_amount(token: str) -> bool:
        return bool(token) and all("0" <= char <= "9" for char in token)

    for index, operation in enumerate(ops):
        tokens = operation.split(" ")
        verb = tokens[0] if tokens else ""
        success = False

        if verb == "open" and len(tokens) == 3:
            _, account, amount = tokens
            if valid_amount(amount) and account not in balances:
                balances[account] = int(amount)
                success = True
                history.append(("open", account))

        elif verb == "deposit" and len(tokens) == 3:
            _, account, amount = tokens
            if valid_amount(amount) and int(amount) > 0 and account in balances:
                value = int(amount)
                balances[account] += value
                success = True
                history.append(("deposit", account, value))

        elif verb == "withdraw" and len(tokens) == 3:
            _, account, amount = tokens
            if valid_amount(amount) and int(amount) > 0 and account in balances:
                value = int(amount)
                if account not in frozen and balances[account] >= value:
                    balances[account] -= value
                    success = True
                    history.append(("withdraw", account, value))

        elif verb == "transfer" and len(tokens) == 4:
            _, source, destination, amount = tokens
            if valid_amount(amount) and int(amount) > 0 and source != destination:
                value = int(amount)
                if (
                    source in balances
                    and destination in balances
                    and source not in frozen
                    and balances[source] >= value
                ):
                    balances[source] -= value
                    balances[destination] += value
                    success = True
                    history.append(("transfer", source, destination, value))

        elif verb == "freeze" and len(tokens) == 2:
            account = tokens[1]
            if account in balances and account not in frozen:
                frozen.add(account)
                success = True
                history.append(("freeze", account))

        elif verb == "unfreeze" and len(tokens) == 2:
            account = tokens[1]
            if account in balances and account in frozen:
                frozen.remove(account)
                success = True
                history.append(("unfreeze", account))

        elif verb == "undo" and len(tokens) == 1:
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
                elif kind == "freeze":
                    frozen.remove(action[1])
                else:  # unfreeze
                    frozen.add(action[1])

                success = True

        if not success:
            rejected.append(index)

    return balances, rejected
