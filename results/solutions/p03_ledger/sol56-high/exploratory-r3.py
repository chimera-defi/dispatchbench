def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    balances: dict[str, int] = {}
    frozen: set[str] = set()
    history: list[tuple] = []
    rejected: list[int] = []

    def parse_amount(token: str) -> int | None:
        if not token or any(ch < "0" or ch > "9" for ch in token):
            return None
        value = 0
        for start in range(0, len(token), 9):
            chunk = token[start:start + 9]
            value = value * (10 ** len(chunk)) + int(chunk)
        return value

    for index, operation in enumerate(ops):
        tokens = operation.split(" ")
        verb = tokens[0]
        success = False

        if verb == "undo" and len(tokens) == 1:
            if history:
                record = history.pop()
                kind = record[0]

                if kind == "open":
                    account = record[1]
                    del balances[account]
                    frozen.discard(account)
                elif kind == "deposit":
                    balances[record[1]] -= record[2]
                elif kind == "withdraw":
                    balances[record[1]] += record[2]
                elif kind == "transfer":
                    source, destination, amount = record[1:]
                    balances[source] += amount
                    balances[destination] -= amount
                elif kind == "freeze":
                    frozen.remove(record[1])
                elif kind == "unfreeze":
                    frozen.add(record[1])

                success = True

        elif verb == "open" and len(tokens) == 3:
            account = tokens[1]
            amount = parse_amount(tokens[2])
            if amount is not None and account not in balances:
                balances[account] = amount
                frozen.discard(account)
                history.append(("open", account))
                success = True

        elif verb == "deposit" and len(tokens) == 3:
            account = tokens[1]
            amount = parse_amount(tokens[2])
            if amount is not None and amount > 0 and account in balances:
                balances[account] += amount
                history.append(("deposit", account, amount))
                success = True

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
                success = True

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
                success = True

        elif verb == "freeze" and len(tokens) == 2:
            account = tokens[1]
            if account in balances and account not in frozen:
                frozen.add(account)
                history.append(("freeze", account))
                success = True

        elif verb == "unfreeze" and len(tokens) == 2:
            account = tokens[1]
            if account in balances and account in frozen:
                frozen.remove(account)
                history.append(("unfreeze", account))
                success = True

        if not success:
            rejected.append(index)

    return balances, rejected
