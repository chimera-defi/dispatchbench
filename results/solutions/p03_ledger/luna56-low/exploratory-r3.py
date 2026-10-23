def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts: dict[str, list[object]] = {}
    history: list[tuple] = []
    rejected: list[int] = []

    def amount(token: str):
        if not token or any(c < "0" or c > "9" for c in token):
            return None
        value = 0
        for c in token:
            value = value * 10 + (ord(c) - 48)
        return value

    for i, operation in enumerate(ops):
        parts = operation.split(" ")
        if not parts:
            rejected.append(i)
            continue

        verb = parts[0]
        success = False
        record = None

        if verb == "open" and len(parts) == 3:
            name, token = parts[1], parts[2]
            n = amount(token)
            if n is not None and name not in accounts:
                accounts[name] = [n, False]
                record = ("close", name)
                success = True

        elif verb == "deposit" and len(parts) == 3:
            name, token = parts[1], parts[2]
            n = amount(token)
            if n is not None and n > 0 and name in accounts:
                accounts[name][0] += n
                record = ("adjust", name, -n)
                success = True

        elif verb == "withdraw" and len(parts) == 3:
            name, token = parts[1], parts[2]
            n = amount(token)
            if (
                n is not None
                and n > 0
                and name in accounts
                and not accounts[name][1]
                and accounts[name][0] >= n
            ):
                accounts[name][0] -= n
                record = ("adjust", name, n)
                success = True

        elif verb == "transfer" and len(parts) == 4:
            source, target, token = parts[1], parts[2], parts[3]
            n = amount(token)
            if (
                n is not None
                and n > 0
                and source != target
                and source in accounts
                and target in accounts
                and not accounts[source][1]
                and accounts[source][0] >= n
            ):
                accounts[source][0] -= n
                accounts[target][0] += n
                record = ("transfer", source, target, n)
                success = True

        elif verb == "freeze" and len(parts) == 2:
            name = parts[1]
            if name in accounts and not accounts[name][1]:
                accounts[name][1] = True
                record = ("state", name, False)
                success = True

        elif verb == "unfreeze" and len(parts) == 2:
            name = parts[1]
            if name in accounts and accounts[name][1]:
                accounts[name][1] = False
                record = ("state", name, True)
                success = True

        elif verb == "undo" and len(parts) == 1:
            if history:
                record = history.pop()
                kind = record[0]

                if kind == "close":
                    del accounts[record[1]]
                elif kind == "adjust":
                    accounts[record[1]][0] += record[2]
                elif kind == "transfer":
                    _, source, target, n = record
                    accounts[source][0] += n
                    accounts[target][0] -= n
                else:
                    _, name, previous = record
                    accounts[name][1] = previous

                success = True

        if success and verb != "undo":
            history.append(record)
        elif not success:
            rejected.append(i)

    return (
        {name: data[0] for name, data in accounts.items()},
        rejected,
    )
