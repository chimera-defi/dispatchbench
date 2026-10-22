def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts: dict[str, list] = {}
    history = []
    rejected = []

    def valid_amount(token: str) -> bool:
        return bool(token) and all("0" <= ch <= "9" for ch in token)

    for i, operation in enumerate(ops):
        tokens = operation.split()
        if not tokens:
            rejected.append(i)
            continue

        verb = tokens[0]
        action = None

        if verb == "open" and len(tokens) == 3:
            _, name, amount_text = tokens
            if valid_amount(amount_text) and name not in accounts:
                accounts[name] = [int(amount_text), False]
                action = ("open", name)

        elif verb == "deposit" and len(tokens) == 3:
            _, name, amount_text = tokens
            if valid_amount(amount_text):
                amount = int(amount_text)
                if amount > 0 and name in accounts:
                    accounts[name][0] += amount
                    action = ("balance", name, -amount)

        elif verb == "withdraw" and len(tokens) == 3:
            _, name, amount_text = tokens
            if valid_amount(amount_text):
                amount = int(amount_text)
                if (amount > 0 and name in accounts
                        and not accounts[name][1]
                        and accounts[name][0] >= amount):
                    accounts[name][0] -= amount
                    action = ("balance", name, amount)

        elif verb == "transfer" and len(tokens) == 4:
            _, source, destination, amount_text = tokens
            if valid_amount(amount_text):
                amount = int(amount_text)
                if (amount > 0 and source != destination
                        and source in accounts and destination in accounts
                        and not accounts[source][1]
                        and accounts[source][0] >= amount):
                    accounts[source][0] -= amount
                    accounts[destination][0] += amount
                    action = ("transfer", source, destination, amount)

        elif verb == "freeze" and len(tokens) == 2:
            name = tokens[1]
            if name in accounts and not accounts[name][1]:
                accounts[name][1] = True
                action = ("frozen", name, False)

        elif verb == "unfreeze" and len(tokens) == 2:
            name = tokens[1]
            if name in accounts and accounts[name][1]:
                accounts[name][1] = False
                action = ("frozen", name, True)

        elif verb == "undo" and len(tokens) == 1:
            if history:
                action_to_revert = history.pop()
                kind = action_to_revert[0]

                if kind == "open":
                    del accounts[action_to_revert[1]]
                elif kind == "balance":
                    _, name, delta = action_to_revert
                    accounts[name][0] += delta
                elif kind == "transfer":
                    _, source, destination, amount = action_to_revert
                    accounts[source][0] += amount
                    accounts[destination][0] -= amount
                elif kind == "frozen":
                    _, name, previous_state = action_to_revert
                    accounts[name][1] = previous_state
            else:
                rejected.append(i)
            continue

        if action is None:
            rejected.append(i)
        else:
            history.append(action)

    balances = {name: account[0] for name, account in accounts.items()}
    return balances, rejected
