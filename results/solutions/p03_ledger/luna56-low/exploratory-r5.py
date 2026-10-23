def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts: dict[str, list[object]] = {}
    history: list[tuple] = []
    rejected: list[int] = []

    def parse_amount(s: str):
        if not s or any(c < "0" or c > "9" for c in s):
            return None
        value = 0
        for c in s:
            value = value * 10 + (ord(c) - 48)
        return value

    for index, operation in enumerate(ops):
        tokens = operation.split()
        if not tokens:
            rejected.append(index)
            continue

        verb = tokens[0]
        success = False
        record = None

        if verb == "open" and len(tokens) == 3:
            name = tokens[1]
            amount = parse_amount(tokens[2])
            if amount is not None and name not in accounts:
                accounts[name] = [amount, False]
                record = ("open", name)
                success = True

        elif verb == "deposit" and len(tokens) == 3:
            name = tokens[1]
            amount = parse_amount(tokens[2])
            if (
                amount is not None
                and amount > 0
                and name in accounts
            ):
                accounts[name][0] += amount
                record = ("deposit", name, amount)
                success = True

        elif verb == "withdraw" and len(tokens) == 3:
            name = tokens[1]
            amount = parse_amount(tokens[2])
            if (
                amount is not None
                and amount > 0
                and name in accounts
                and not accounts[name][1]
                and accounts[name][0] >= amount
            ):
                accounts[name][0] -= amount
                record = ("withdraw", name, amount)
                success = True

        elif verb == "transfer" and len(tokens) == 4:
            source, target = tokens[1], tokens[2]
            amount = parse_amount(tokens[3])
            if (
                amount is not None
                and amount > 0
                and source != target
                and source in accounts
                and target in accounts
                and not accounts[source][1]
                and accounts[source][0] >= amount
            ):
                accounts[source][0] -= amount
                accounts[target][0] += amount
                record = ("transfer", source, target, amount)
                success = True

        elif verb == "freeze" and len(tokens) == 2:
            name = tokens[1]
            if name in accounts and not accounts[name][1]:
                accounts[name][1] = True
                record = ("freeze", name)
                success = True

        elif verb == "unfreeze" and len(tokens) == 2:
            name = tokens[1]
            if name in accounts and accounts[name][1]:
                accounts[name][1] = False
                record = ("unfreeze", name)
                success = True

        elif verb == "undo" and len(tokens) == 1:
            if history:
                record = history.pop()
                kind = record[0]

                if kind == "open":
                    del accounts[record[1]]
                elif kind == "deposit":
                    accounts[record[1]][0] -= record[2]
                elif kind == "withdraw":
                    accounts[record[1]][0] += record[2]
                elif kind == "transfer":
                    _, source, target, amount = record
                    accounts[source][0] += amount
                    accounts[target][0] -= amount
                elif kind == "freeze":
                    accounts[record[1]][1] = False
                elif kind == "unfreeze":
                    accounts[record[1]][1] = True

                success = True

        if not success:
            rejected.append(index)
        elif verb != "undo":
            history.append(record)

    return (
        {name: state[0] for name, state in accounts.items()},
        rejected,
    )
