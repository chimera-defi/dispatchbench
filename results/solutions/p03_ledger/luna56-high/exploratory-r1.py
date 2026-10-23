def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts: dict[str, list[object]] = {}
    history: list[tuple] = []
    rejected: list[int] = []

    def parse_amount(s: str):
        if not s:
            return None
        value = 0
        for ch in s:
            if ch < "0" or ch > "9":
                return None
            value = value * 10 + ord(ch) - ord("0")
        return value

    for index, operation in enumerate(ops):
        tokens = operation.split(" ")
        verb = tokens[0] if tokens else ""

        if verb == "open" and len(tokens) == 3:
            name = tokens[1]
            amount = parse_amount(tokens[2])
            if amount is not None and name not in accounts:
                accounts[name] = [amount, False]
                history.append(("open", name))
                continue

        elif verb == "deposit" and len(tokens) == 3:
            name = tokens[1]
            amount = parse_amount(tokens[2])
            if amount is not None and amount > 0 and name in accounts:
                accounts[name][0] += amount
                history.append(("deposit", name, amount))
                continue

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
                continue

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
                continue

        elif verb == "freeze" and len(tokens) == 2:
            name = tokens[1]
            if name in accounts and not accounts[name][1]:
                accounts[name][1] = True
                history.append(("freeze", name))
                continue

        elif verb == "unfreeze" and len(tokens) == 2:
            name = tokens[1]
            if name in accounts and accounts[name][1]:
                accounts[name][1] = False
                history.append(("unfreeze", name))
                continue

        elif verb == "undo" and len(tokens) == 1:
            if history:
                action = history.pop()
                kind = action[0]

                if kind == "open":
                    del accounts[action[1]]
                elif kind == "deposit":
                    accounts[action[1]][0] -= action[2]
                elif kind == "withdraw":
                    accounts[action[1]][0] += action[2]
                elif kind == "transfer":
                    source, target, amount = action[1], action[2], action[3]
                    accounts[source][0] += amount
                    accounts[target][0] -= amount
                elif kind == "freeze":
                    accounts[action[1]][1] = False
                else:  # unfreeze
                    accounts[action[1]][1] = True

                continue

        rejected.append(index)

    return {name: data[0] for name, data in accounts.items()}, rejected
