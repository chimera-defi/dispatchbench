def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts: dict[str, list[object]] = {}
    history: list[tuple] = []
    rejected: list[int] = []

    def parse_amount(token: str):
        if not token:
            return None
        value = 0
        for ch in token:
            if ch < "0" or ch > "9":
                return None
            value = value * 10 + (ord(ch) - ord("0"))
        return value

    for index, operation in enumerate(ops):
        parts = operation.split(" ")
        verb = parts[0] if parts else ""

        if verb == "open" and len(parts) == 3:
            name = parts[1]
            amount = parse_amount(parts[2])
            if amount is not None and name not in accounts:
                accounts[name] = [amount, False]
                history.append(("open", name))
            else:
                rejected.append(index)

        elif verb == "deposit" and len(parts) == 3:
            name = parts[1]
            amount = parse_amount(parts[2])
            if amount is not None and amount > 0 and name in accounts:
                accounts[name][0] += amount
                history.append(("deposit", name, amount))
            else:
                rejected.append(index)

        elif verb == "withdraw" and len(parts) == 3:
            name = parts[1]
            amount = parse_amount(parts[2])
            if (
                amount is not None
                and amount > 0
                and name in accounts
                and not accounts[name][1]
                and accounts[name][0] >= amount
            ):
                accounts[name][0] -= amount
                history.append(("withdraw", name, amount))
            else:
                rejected.append(index)

        elif verb == "transfer" and len(parts) == 4:
            source, target = parts[1], parts[2]
            amount = parse_amount(parts[3])
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
            else:
                rejected.append(index)

        elif verb == "freeze" and len(parts) == 2:
            name = parts[1]
            if name in accounts and not accounts[name][1]:
                accounts[name][1] = True
                history.append(("freeze", name))
            else:
                rejected.append(index)

        elif verb == "unfreeze" and len(parts) == 2:
            name = parts[1]
            if name in accounts and accounts[name][1]:
                accounts[name][1] = False
                history.append(("unfreeze", name))
            else:
                rejected.append(index)

        elif verb == "undo" and len(parts) == 1:
            if not history:
                rejected.append(index)
            else:
                action = history.pop()
                kind = action[0]

                if kind == "open":
                    del accounts[action[1]]
                elif kind == "deposit":
                    accounts[action[1]][0] -= action[2]
                elif kind == "withdraw":
                    accounts[action[1]][0] += action[2]
                elif kind == "transfer":
                    accounts[action[1]][0] += action[3]
                    accounts[action[2]][0] -= action[3]
                elif kind == "freeze":
                    accounts[action[1]][1] = False
                else:
                    accounts[action[1]][1] = True
        else:
            rejected.append(index)

    balances = {name: data[0] for name, data in accounts.items()}
    return balances, rejected
