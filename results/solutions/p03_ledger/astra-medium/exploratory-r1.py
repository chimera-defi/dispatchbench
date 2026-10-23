def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    balances = {}
    frozen = set()
    history = []
    rejected = []

    arities = {
        "open": 3,
        "deposit": 3,
        "withdraw": 3,
        "transfer": 4,
        "freeze": 2,
        "unfreeze": 2,
        "undo": 1,
    }

    def parse_amount(token):
        if not token or any(c < "0" or c > "9" for c in token):
            return None
        # Small chunks avoid Python's limit on decimal string conversion.
        value = 0
        for start in range(0, len(token), 9):
            chunk = token[start:start + 9]
            value = value * (10 ** len(chunk)) + int(chunk)
        return value

    def snapshot(name):
        return name, balances.get(name), name in frozen

    for index, operation in enumerate(ops):
        tokens = operation.split(" ")
        verb = tokens[0]

        if (
            verb not in arities
            or len(tokens) != arities[verb]
            or any(token == "" for token in tokens)
        ):
            rejected.append(index)
            continue

        if verb == "undo":
            if not history:
                rejected.append(index)
                continue

            for name, balance, was_frozen in history.pop():
                if balance is None:
                    balances.pop(name, None)
                else:
                    balances[name] = balance

                if was_frozen:
                    frozen.add(name)
                else:
                    frozen.discard(name)
            continue

        account = tokens[1]

        if verb in ("freeze", "unfreeze"):
            valid = account in balances and (
                (verb == "freeze" and account not in frozen)
                or (verb == "unfreeze" and account in frozen)
            )
            if not valid:
                rejected.append(index)
                continue

            history.append((snapshot(account),))
            if verb == "freeze":
                frozen.add(account)
            else:
                frozen.remove(account)
            continue

        amount = parse_amount(tokens[-1])
        if amount is None or (verb != "open" and amount == 0):
            rejected.append(index)
            continue

        if verb == "open":
            if account in balances:
                rejected.append(index)
                continue
            history.append((snapshot(account),))
            balances[account] = amount

        elif verb == "deposit":
            if account not in balances:
                rejected.append(index)
                continue
            history.append((snapshot(account),))
            balances[account] += amount

        elif verb == "withdraw":
            if (
                account not in balances
                or account in frozen
                or balances[account] < amount
            ):
                rejected.append(index)
                continue
            history.append((snapshot(account),))
            balances[account] -= amount

        else:  # transfer
            destination = tokens[2]
            if (
                account == destination
                or account not in balances
                or destination not in balances
                or account in frozen
                or balances[account] < amount
            ):
                rejected.append(index)
                continue
            history.append((snapshot(account), snapshot(destination)))
            balances[account] -= amount
            balances[destination] += amount

    return balances, rejected
