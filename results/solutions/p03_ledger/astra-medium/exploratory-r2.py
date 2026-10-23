def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts = {}
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

    for index, operation in enumerate(ops):
        tokens = operation.split(" ")
        verb = tokens[0]

        if verb not in arities or len(tokens) != arities[verb]:
            rejected.append(index)
            continue

        if verb == "undo":
            if not history:
                rejected.append(index)
                continue
            for name, previous in history.pop():
                if previous is None:
                    del accounts[name]
                else:
                    accounts[name] = previous
            continue

        name = tokens[1]

        if verb in ("freeze", "unfreeze"):
            target = verb == "freeze"
            if name not in accounts or accounts[name][1] == target:
                rejected.append(index)
                continue
            previous = accounts[name]
            history.append(((name, previous),))
            accounts[name] = (previous[0], target)
            continue

        amount_text = tokens[-1]
        if not amount_text or any(c < "0" or c > "9" for c in amount_text):
            rejected.append(index)
            continue

        # Small chunks avoid Python's limit on decimal string conversions.
        amount = 0
        for start in range(0, len(amount_text), 9):
            chunk = amount_text[start:start + 9]
            amount = amount * (10 ** len(chunk)) + int(chunk)

        if verb == "open":
            if name in accounts:
                rejected.append(index)
                continue
            history.append(((name, None),))
            accounts[name] = (amount, False)
            continue

        if amount == 0 or name not in accounts:
            rejected.append(index)
            continue

        previous = accounts[name]
        balance, frozen = previous

        if verb == "deposit":
            history.append(((name, previous),))
            accounts[name] = (balance + amount, frozen)
            continue

        if frozen or balance < amount:
            rejected.append(index)
            continue

        if verb == "withdraw":
            history.append(((name, previous),))
            accounts[name] = (balance - amount, frozen)
            continue

        destination = tokens[2]
        if destination == name or destination not in accounts:
            rejected.append(index)
            continue

        destination_previous = accounts[destination]
        history.append((
            (name, previous),
            (destination, destination_previous),
        ))
        accounts[name] = (balance - amount, frozen)
        accounts[destination] = (
            destination_previous[0] + amount,
            destination_previous[1],
        )

    return {name: state[0] for name, state in accounts.items()}, rejected
