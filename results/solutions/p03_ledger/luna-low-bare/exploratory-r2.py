def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    balances = {}
    frozen = set()
    history = []
    rejected = []

    for index, operation in enumerate(ops):
        tokens = operation.split()
        if not tokens:
            rejected.append(index)
            continue

        verb = tokens[0]

        if verb == "undo":
            if len(tokens) != 1 or not history:
                rejected.append(index)
                continue

            action = history.pop()
            kind = action[0]

            if kind == "open":
                _, account = action
                del balances[account]
                frozen.discard(account)
            elif kind == "balance":
                _, account, previous = action
                balances[account] = previous
            elif kind == "freeze":
                _, account, was_frozen = action
                if was_frozen:
                    frozen.add(account)
                else:
                    frozen.discard(account)
            continue

        if verb == "open":
            if len(tokens) != 3:
                rejected.append(index)
                continue
            account, amount_text = tokens[1], tokens[2]
            if not amount_text.isdigit() or account in balances:
                rejected.append(index)
                continue
            balances[account] = int(amount_text)
            history.append(("open", account))

        elif verb == "deposit" or verb == "withdraw":
            if len(tokens) != 3:
                rejected.append(index)
                continue
            account, amount_text = tokens[1], tokens[2]
            if (not amount_text.isdigit() or account not in balances
                    or int(amount_text) <= 0):
                rejected.append(index)
                continue
            amount = int(amount_text)
            if verb == "withdraw":
                if account in frozen or balances[account] < amount:
                    rejected.append(index)
                    continue
                balances[account] -= amount
            else:
                balances[account] += amount
            history.append(("balance", account, balances[account] - amount if verb == "deposit"
                            else balances[account] + amount))

        elif verb == "transfer":
            if len(tokens) != 4:
                rejected.append(index)
                continue
            source, target, amount_text = tokens[1], tokens[2], tokens[3]
            if (not amount_text.isdigit() or int(amount_text) <= 0
                    or source == target or source not in balances
                    or target not in balances or source in frozen):
                rejected.append(index)
                continue
            amount = int(amount_text)
            if balances[source] < amount:
                rejected.append(index)
                continue
            history.append(("balance", source, balances[source]))
            history.append(("balance", target, balances[target]))
            balances[source] -= amount
            balances[target] += amount

        elif verb == "freeze" or verb == "unfreeze":
            if len(tokens) != 2:
                rejected.append(index)
                continue
            account = tokens[1]
            if account not in balances:
                rejected.append(index)
                continue
            was_frozen = account in frozen
            if (verb == "freeze" and was_frozen) or (verb == "unfreeze" and not was_frozen):
                rejected.append(index)
                continue
            history.append(("freeze", account, was_frozen))
            if verb == "freeze":
                frozen.add(account)
            else:
                frozen.remove(account)

        else:
            rejected.append(index)

    return balances, rejected
