def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts = {}  # name -> (balance, frozen)
    history = []
    rejected = []
    arity = {
        "open": 3,
        "deposit": 3,
        "withdraw": 3,
        "transfer": 4,
        "freeze": 2,
        "unfreeze": 2,
        "undo": 1,
    }

    def parse_amount(s):
        if not s or any(c < "0" or c > "9" for c in s):
            return None
        # Chunk conversion also supports amounts beyond Python's
        # configurable limit for converting long decimal strings.
        value = 0
        for start in range(0, len(s), 1000):
            chunk = s[start:start + 1000]
            value = value * (10 ** len(chunk)) + int(chunk)
        return value

    for index, operation in enumerate(ops):
        tokens = operation.split(" ")
        verb = tokens[0]
        if verb not in arity or len(tokens) != arity[verb]:
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
            previous = accounts.get(name)
            target_frozen = verb == "freeze"
            if previous is None or previous[1] == target_frozen:
                rejected.append(index)
                continue
            history.append(((name, previous),))
            accounts[name] = (previous[0], target_frozen)
            continue

        amount = parse_amount(tokens[-1])
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

        destination = tokens[2]
        destination_previous = accounts.get(destination)
        if destination == name or destination_previous is None:
            rejected.append(index)
            continue

        history.append(
            ((name, previous), (destination, destination_previous))
        )
        accounts[name] = (balance - amount, frozen)
        accounts[destination] = (
            destination_previous[0] + amount,
            destination_previous[1],
        )

    return {name: state[0] for name, state in accounts.items()}, rejected
