def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts: dict[str, list[int | bool]] = {}
    history: list[tuple] = []
    rejected: list[int] = []

    def valid_amount(s: str) -> bool:
        return bool(s) and all("0" <= ch <= "9" for ch in s)

    for index, operation in enumerate(ops):
        parts = operation.split(" ")
        verb = parts[0] if parts else ""

        if verb == "undo":
            if len(parts) != 1 or not history:
                rejected.append(index)
                continue

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
            else:  # unfreeze
                accounts[action[1]][1] = True
            continue

        success = False

        if verb == "open" and len(parts) == 3:
            name, amount_text = parts[1], parts[2]
            if valid_amount(amount_text) and name not in accounts:
                accounts[name] = [int(amount_text), False]
                history.append(("open", name))
                success = True

        elif verb == "deposit" and len(parts) == 3:
            name, amount_text = parts[1], parts[2]
            if (
                valid_amount(amount_text)
                and int(amount_text) > 0
                and name in accounts
            ):
                amount = int(amount_text)
                accounts[name][0] += amount
                history.append(("deposit", name, amount))
                success = True

        elif verb == "withdraw" and len(parts) == 3:
            name, amount_text = parts[1], parts[2]
            if valid_amount(amount_text) and name in accounts:
                amount = int(amount_text)
                if (
                    amount > 0
                    and not accounts[name][1]
                    and accounts[name][0] >= amount
                ):
                    accounts[name][0] -= amount
                    history.append(("withdraw", name, amount))
                    success = True

        elif verb == "transfer" and len(parts) == 4:
            source, target, amount_text = parts[1], parts[2], parts[3]
            if (
                valid_amount(amount_text)
                and source != target
                and source in accounts
                and target in accounts
            ):
                amount = int(amount_text)
                if (
                    amount > 0
                    and not accounts[source][1]
                    and accounts[source][0] >= amount
                ):
                    accounts[source][0] -= amount
                    accounts[target][0] += amount
                    history.append(("transfer", source, target, amount))
                    success = True

        elif verb == "freeze" and len(parts) == 2:
            name = parts[1]
            if name in accounts and not accounts[name][1]:
                accounts[name][1] = True
                history.append(("freeze", name))
                success = True

        elif verb == "unfreeze" and len(parts) == 2:
            name = parts[1]
            if name in accounts and accounts[name][1]:
                accounts[name][1] = False
                history.append(("unfreeze", name))
                success = True

        if not success:
            rejected.append(index)

    return {name: data[0] for name, data in accounts.items()}, rejected
