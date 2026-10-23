def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts: dict[str, list[int | bool]] = {}
    history: list[tuple] = []
    rejected: list[int] = []

    def valid_amount(value: str) -> bool:
        return bool(value) and all("0" <= char <= "9" for char in value)

    for index, operation in enumerate(ops):
        tokens = operation.split(" ")
        verb = tokens[0] if tokens else ""
        success = False

        if verb == "open" and len(tokens) == 3:
            name, raw_amount = tokens[1], tokens[2]
            if name not in accounts and valid_amount(raw_amount):
                amount = int(raw_amount)
                accounts[name] = [amount, False]
                history.append(("open", name))
                success = True

        elif verb == "deposit" and len(tokens) == 3:
            name, raw_amount = tokens[1], tokens[2]
            if name in accounts and valid_amount(raw_amount):
                amount = int(raw_amount)
                if amount > 0:
                    accounts[name][0] += amount
                    history.append(("deposit", name, amount))
                    success = True

        elif verb == "withdraw" and len(tokens) == 3:
            name, raw_amount = tokens[1], tokens[2]
            if name in accounts and valid_amount(raw_amount):
                amount = int(raw_amount)
                balance, frozen = accounts[name]
                if amount > 0 and not frozen and balance >= amount:
                    accounts[name][0] -= amount
                    history.append(("withdraw", name, amount))
                    success = True

        elif verb == "transfer" and len(tokens) == 4:
            source, destination, raw_amount = tokens[1], tokens[2], tokens[3]
            if (
                source != destination
                and source in accounts
                and destination in accounts
                and valid_amount(raw_amount)
            ):
                amount = int(raw_amount)
                balance, frozen = accounts[source]
                if amount > 0 and not frozen and balance >= amount:
                    accounts[source][0] -= amount
                    accounts[destination][0] += amount
                    history.append(("transfer", source, destination, amount))
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

        elif verb == "undo" and len(tokens) == 1:
            if history:
                record = history.pop()
                action = record[0]

                if action == "open":
                    del accounts[record[1]]
                elif action == "deposit":
                    accounts[record[1]][0] -= record[2]
                elif action == "withdraw":
                    accounts[record[1]][0] += record[2]
                elif action == "transfer":
                    accounts[record[1]][0] += record[3]
                    accounts[record[2]][0] -= record[3]
                elif action == "freeze":
                    accounts[record[1]][1] = False
                elif action == "unfreeze":
                    accounts[record[1]][1] = True

                success = True

        if not success:
            rejected.append(index)

    balances = {name: int(data[0]) for name, data in accounts.items()}
    return balances, rejected
