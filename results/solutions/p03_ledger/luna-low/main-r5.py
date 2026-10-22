def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts = {}
    history = []
    rejected = []

    for index, operation in enumerate(ops):
        tokens = operation.split()
        success = False

        if tokens:
            verb = tokens[0]

            if verb == "open" and len(tokens) == 3:
                _, name, raw_amount = tokens
                if raw_amount.isascii() and raw_amount.isdigit() and name not in accounts:
                    accounts[name] = [int(raw_amount), False]
                    history.append(("open", name))
                    success = True

            elif verb == "deposit" and len(tokens) == 3:
                _, name, raw_amount = tokens
                if raw_amount.isascii() and raw_amount.isdigit():
                    amount = int(raw_amount)
                    if amount > 0 and name in accounts:
                        accounts[name][0] += amount
                        history.append(("balance", name, -amount))
                        success = True

            elif verb == "withdraw" and len(tokens) == 3:
                _, name, raw_amount = tokens
                if raw_amount.isascii() and raw_amount.isdigit():
                    amount = int(raw_amount)
                    if (amount > 0 and name in accounts and
                            not accounts[name][1] and accounts[name][0] >= amount):
                        accounts[name][0] -= amount
                        history.append(("balance", name, amount))
                        success = True

            elif verb == "transfer" and len(tokens) == 4:
                _, source, target, raw_amount = tokens
                if raw_amount.isascii() and raw_amount.isdigit():
                    amount = int(raw_amount)
                    if (amount > 0 and source != target and source in accounts and
                            target in accounts and not accounts[source][1] and
                            accounts[source][0] >= amount):
                        accounts[source][0] -= amount
                        accounts[target][0] += amount
                        history.append(("transfer", source, target, amount))
                        success = True

            elif verb == "freeze" and len(tokens) == 2:
                name = tokens[1]
                if name in accounts and not accounts[name][1]:
                    accounts[name][1] = True
                    history.append(("frozen", name, False))
                    success = True

            elif verb == "unfreeze" and len(tokens) == 2:
                name = tokens[1]
                if name in accounts and accounts[name][1]:
                    accounts[name][1] = False
                    history.append(("frozen", name, True))
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
                        accounts[change[1]][1] = change[2]
                    success = True

        if not success:
            rejected.append(index)

    balances = {name: data[0] for name, data in accounts.items()}
    return balances, rejected
