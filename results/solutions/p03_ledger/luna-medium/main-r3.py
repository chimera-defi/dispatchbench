def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts: dict[str, list] = {}
    history: list[tuple] = []
    rejected: list[int] = []

    for i, operation in enumerate(ops):
        tokens = operation.split()
        if not tokens:
            rejected.append(i)
            continue

        verb = tokens[0]
        success = False
        action = None

        if verb == "open" and len(tokens) == 3:
            name, amount_text = tokens[1], tokens[2]
            if amount_text.isdigit():
                amount = int(amount_text)
                if name not in accounts:
                    accounts[name] = [amount, False]
                    action = ("open", name)
                    success = True

        elif verb == "deposit" and len(tokens) == 3:
            name, amount_text = tokens[1], tokens[2]
            if amount_text.isdigit():
                amount = int(amount_text)
                if amount > 0 and name in accounts:
                    accounts[name][0] += amount
                    action = ("balance", name, -amount)
                    success = True

        elif verb == "withdraw" and len(tokens) == 3:
            name, amount_text = tokens[1], tokens[2]
            if amount_text.isdigit():
                amount = int(amount_text)
                if (amount > 0 and name in accounts and
                        not accounts[name][1] and accounts[name][0] >= amount):
                    accounts[name][0] -= amount
                    action = ("balance", name, amount)
                    success = True

        elif verb == "transfer" and len(tokens) == 4:
            src, dst, amount_text = tokens[1], tokens[2], tokens[3]
            if amount_text.isdigit():
                amount = int(amount_text)
                if (amount > 0 and src != dst and src in accounts and
                        dst in accounts and not accounts[src][1] and
                        accounts[src][0] >= amount):
                    accounts[src][0] -= amount
                    accounts[dst][0] += amount
                    action = ("transfer", src, dst, amount)
                    success = True

        elif verb in ("freeze", "unfreeze") and len(tokens) == 2:
            name = tokens[1]
            if name in accounts:
                frozen = accounts[name][1]
                if (verb == "freeze" and not frozen) or (verb == "unfreeze" and frozen):
                    accounts[name][1] = verb == "freeze"
                    action = ("frozen", name, frozen)
                    success = True

        elif verb == "undo" and len(tokens) == 1:
            if history:
                action = history.pop()
                kind = action[0]
                if kind == "open":
                    del accounts[action[1]]
                elif kind == "balance":
                    accounts[action[1]][0] += action[2]
                elif kind == "transfer":
                    _, src, dst, amount = action
                    accounts[src][0] += amount
                    accounts[dst][0] -= amount
                elif kind == "frozen":
                    _, name, previous = action
                    accounts[name][1] = previous
                success = True

        if success:
            if verb != "undo":
                history.append(action)
        else:
            rejected.append(i)

    balances = {name: state[0] for name, state in accounts.items()}
    return balances, rejected
