def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts = {}
    rejected = []
    history = []

    for index, operation in enumerate(ops):
        tokens = operation.split(" ")
        verb = tokens[0] if tokens else ""
        success = False
        change = None

        if verb == "open" and len(tokens) == 3:
            _, account, raw_amount = tokens
            if raw_amount.isdigit() and all("0" <= ch <= "9" for ch in raw_amount) and account not in accounts:
                amount = int(raw_amount)
                accounts[account] = [amount, False]
                change = ("open", account)
                success = True

        elif verb == "deposit" and len(tokens) == 3:
            _, account, raw_amount = tokens
            if raw_amount.isdigit() and all("0" <= ch <= "9" for ch in raw_amount):
                amount = int(raw_amount)
                if amount > 0 and account in accounts:
                    accounts[account][0] += amount
                    change = ("balance", account, -amount)
                    success = True

        elif verb == "withdraw" and len(tokens) == 3:
            _, account, raw_amount = tokens
            if raw_amount.isdigit() and all("0" <= ch <= "9" for ch in raw_amount):
                amount = int(raw_amount)
                if amount > 0 and account in accounts and not accounts[account][1] and accounts[account][0] >= amount:
                    accounts[account][0] -= amount
                    change = ("balance", account, amount)
                    success = True

        elif verb == "transfer" and len(tokens) == 4:
            _, source, target, raw_amount = tokens
            if raw_amount.isdigit() and all("0" <= ch <= "9" for ch in raw_amount):
                amount = int(raw_amount)
                if (amount > 0 and source != target and source in accounts and target in accounts
                        and not accounts[source][1] and accounts[source][0] >= amount):
                    accounts[source][0] -= amount
                    accounts[target][0] += amount
                    change = ("transfer", source, target, amount)
                    success = True

        elif verb == "freeze" and len(tokens) == 2:
            account = tokens[1]
            if account in accounts and not accounts[account][1]:
                accounts[account][1] = True
                change = ("frozen", account, False)
                success = True

        elif verb == "unfreeze" and len(tokens) == 2:
            account = tokens[1]
            if account in accounts and accounts[account][1]:
                accounts[account][1] = False
                change = ("frozen", account, True)
                success = True

        elif verb == "undo" and len(tokens) == 1:
            if history:
                change = history.pop()
                kind = change[0]
                if kind == "open":
                    del accounts[change[1]]
                elif kind == "balance":
                    accounts[change[1]][0] += change[2]
                elif kind == "transfer":
                    _, source, target, amount = change
                    accounts[source][0] += amount
                    accounts[target][0] -= amount
                elif kind == "frozen":
                    _, account, previous = change
                    accounts[account][1] = previous
                success = True

        if success:
            if verb != "undo":
                history.append(change)
        else:
            rejected.append(index)

    balances = {account: state[0] for account, state in accounts.items()}
    return balances, rejected
