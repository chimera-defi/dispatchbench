def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts = {}  # name -> (balance, frozen)
    history = []
    rejected = []

    def parse_amount(text):
        if not text or any(c < "0" or c > "9" for c in text):
            return None
        value = 0
        for start in range(0, len(text), 9):
            chunk = text[start:start + 9]
            value = value * (10 ** len(chunk)) + int(chunk)
        return value

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
        parts = operation.split(" ")
        verb = parts[0]

        if (
            any(part == "" for part in parts)
            or verb not in arities
            or len(parts) != arities[verb]
        ):
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

        name = parts[1]

        if verb in ("freeze", "unfreeze"):
            previous = accounts.get(name)
            target = verb == "freeze"
            if previous is None or previous[1] == target:
                rejected.append(index)
                continue
            history.append(((name, previous),))
            accounts[name] = (previous[0], target)
            continue

        amount = parse_amount(parts[-1])
        if amount is None or (verb != "open" and amount == 0):
            rejected.append(index)
            continue

        if verb == "open":
            if name in accounts:
                rejected.append(index)
                continue
            history.append(((name, None),))
            accounts[name] = (amount, False)
            continue

        previous = accounts.get(name)
        if previous is None:
            rejected.append(index)
            continue

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

        destination = parts[2]
        destination_previous = accounts.get(destination)
        if destination == name or destination_previous is None:
            rejected.append(index)
            continue

        history.append((
            (name, previous),
            (destination, destination_previous),
        ))
        accounts[name] = (balance - amount, frozen)
        accounts[destination] = (
            destination_previous[0] + amount,
            destination_previous[1],
        )

    return {
        name: state[0] for name, state in accounts.items()
    }, rejected
