def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    balances: dict[str, int] = {}
    frozen: set[str] = set()
    history: list[tuple] = []
    rejected: list[int] = []

    def parse_amount(token: str):
        if not token:
            return None
        value = 0
        for char in token:
            if char < "0" or char > "9":
                return None
            value = value * 10 + (ord(char) - ord("0"))
        return value

    for index, operation in enumerate(ops):
        tokens = operation.split(" ")
        verb = tokens[0]
        succeeded = False

        if verb == "open" and len(tokens) == 3:
            account = tokens[1]
            amount = parse_amount(tokens[2])
            if amount is not None and account not in balances:
                balances[account] = amount
                history.append(("open", account))
                succeeded = True

        elif verb == "deposit" and len(tokens) == 3:
            account = tokens[1]
            amount = parse_amount(tokens[2])
            if amount is not None and amount > 0 and account in balances:
                balances[account] += amount
                history.append(("deposit", account, amount))
                succeeded = True

        elif verb == "withdraw" and len(tokens) == 3:
            account = tokens[1]
            amount = parse_amount(tokens[2])
            if (
                amount is not None
                and amount > 0
                and account in balances
                and account not in frozen
                and balances[account] >= amount
            ):
                balances[account] -= amount
                history.append(("withdraw", account, amount))
                succeeded = True

        elif verb == "transfer" and len(tokens) == 4:
            source, destination = tokens[1], tokens[2]
            amount = parse_amount(tokens[3])
            if (
                amount is not None
                and amount > 0
                and source != destination
                and source in balances
                and destination in balances
                and source not in frozen
                and balances[source] >= amount
            ):
                balances[source] -= amount
                balances[destination] += amount
                history.append(("transfer", source, destination, amount))
                succeeded = True

        elif verb == "freeze" and len(tokens) == 2:
            account = tokens[1]
            if account in balances and account not in frozen:
                frozen.add(account)
                history.append(("freeze", account))
                succeeded = True

        elif verb == "unfreeze" and len(tokens) == 2:
            account = tokens[1]
            if account in balances and account in frozen:
                frozen.remove(account)
                history.append(("unfreeze", account))
                succeeded = True

        elif verb == "undo" and len(tokens) == 1:
            if history:
                record = history.pop()
                action = record[0]

                if action == "open":
                    account = record[1]
                    del balances[account]
                    frozen.discard(account)
                elif action == "deposit":
                    _, account, amount = record
                    balances[account] -= amount
                elif action == "withdraw":
                    _, account, amount = record
                    balances[account] += amount
                elif action == "transfer":
                    _, source, destination, amount = record
                    balances[source] += amount
                    balances[destination] -= amount
                elif action == "freeze":
                    frozen.remove(record[1])
                elif action == "unfreeze":
                    frozen.add(record[1])

                succeeded = True

        if not succeeded:
            rejected.append(index)

    return balances, rejected
