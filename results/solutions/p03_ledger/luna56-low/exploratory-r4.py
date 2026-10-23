def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    balances: dict[str, int] = {}
    frozen: set[str] = set()
    history: list[tuple] = []
    rejected: list[int] = []

    def parse_amount(token: str):
        if not token or any(c < "0" or c > "9" for c in token):
            return None
        return int(token)

    for i, operation in enumerate(ops):
        tokens = operation.split()
        if not tokens:
            rejected.append(i)
            continue

        verb = tokens[0]
        success = False
        record = None

        if verb == "open" and len(tokens) == 3:
            account, token = tokens[1], tokens[2]
            amount = parse_amount(token)
            if amount is not None and account not in balances:
                balances[account] = amount
                success = True
                record = ("open", account)

        elif verb == "deposit" and len(tokens) == 3:
            account, token = tokens[1], tokens[2]
            amount = parse_amount(token)
            if (
                amount is not None
                and amount > 0
                and account in balances
            ):
                balances[account] += amount
                success = True
                record = ("deposit", account, amount)

        elif verb == "withdraw" and len(tokens) == 3:
            account, token = tokens[1], tokens[2]
            amount = parse_amount(token)
            if (
                amount is not None
                and amount > 0
                and account in balances
                and account not in frozen
                and balances[account] >= amount
            ):
                balances[account] -= amount
                success = True
                record = ("withdraw", account, amount)

        elif verb == "transfer" and len(tokens) == 4:
            source, target, token = tokens[1], tokens[2], tokens[3]
            amount = parse_amount(token)
            if (
                amount is not None
                and amount > 0
                and source != target
                and source in balances
                and target in balances
                and source not in frozen
                and balances[source] >= amount
            ):
                balances[source] -= amount
                balances[target] += amount
                success = True
                record = ("transfer", source, target, amount)

        elif verb == "freeze" and len(tokens) == 2:
            account = tokens[1]
            if account in balances and account not in frozen:
                frozen.add(account)
                success = True
                record = ("freeze", account)

        elif verb == "unfreeze" and len(tokens) == 2:
            account = tokens[1]
            if account in balances and account in frozen:
                frozen.remove(account)
                success = True
                record = ("unfreeze", account)

        elif verb == "undo" and len(tokens) == 1:
            if history:
                record = history.pop()
                kind = record[0]

                if kind == "open":
                    del balances[record[1]]
                    frozen.discard(record[1])
                elif kind == "deposit":
                    balances[record[1]] -= record[2]
                elif kind == "withdraw":
                    balances[record[1]] += record[2]
                elif kind == "transfer":
                    _, source, target, amount = record
                    balances[source] += amount
                    balances[target] -= amount
                elif kind == "freeze":
                    frozen.remove(record[1])
                elif kind == "unfreeze":
                    frozen.add(record[1])

                success = True

        if not success:
            rejected.append(i)
        elif verb != "undo":
            history.append(record)

    return balances, rejected
