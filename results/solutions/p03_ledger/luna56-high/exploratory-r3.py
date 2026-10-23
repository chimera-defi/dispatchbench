def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts: dict[str, list[object]] = {}
    history: list[tuple] = []
    rejected: list[int] = []

    def parse_amount(s: str) -> int | None:
        if not s or any(c < "0" or c > "9" for c in s):
            return None
        value = 0
        for c in s:
            value = value * 10 + (ord(c) - 48)
        return value

    for index, operation in enumerate(ops):
        tokens = operation.split(" ")
        verb = tokens[0] if tokens else ""

        if verb == "undo":
            if len(tokens) != 1 or not history:
                rejected.append(index)
                continue

            entry = history.pop()
            kind = entry[0]

            if kind == "open":
                del accounts[entry[1]]
            elif kind == "deposit":
                accounts[entry[1]][0] -= entry[2]
            elif kind == "withdraw":
                accounts[entry[1]][0] += entry[2]
            elif kind == "transfer":
                accounts[entry[1]][0] += entry[3]
                accounts[entry[2]][0] -= entry[3]
            elif kind == "freeze":
                accounts[entry[1]][1] = False
            else:  # unfreeze
                accounts[entry[1]][1] = True
            continue

        success = False

        if verb == "open" and len(tokens) == 3:
            name = tokens[1]
            amount = parse_amount(tokens[2])
            if amount is not None and name not in accounts:
                accounts[name] = [amount, False]
                history.append(("open", name))
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
                history.append(("deposit", name, amount))
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
                history.append(("withdraw", name, amount))
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
                history.append(("transfer", source, target, amount))
                success = True

        elif verb == "freeze" and len(tokens) == 2:
            name = tokens[1]
            if name in accounts and not accounts[name][1]:
                accounts[name][1] = True
                history.append(("freeze", name))
                success = True

        elif verb == "unfreeze" and len(tokens) == 2:
            name = tokens[1]
            if name in accounts and accounts[name][1]:
                accounts[name][1] = False
                history.append(("unfreeze", name))
                success = True

        if not success:
            rejected.append(index)

    balances = {name: data[0] for name, data in accounts.items()}
    return balances, rejected
