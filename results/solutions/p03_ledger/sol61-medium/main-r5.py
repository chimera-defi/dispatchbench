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

        # Small chunks also support amounts exceeding Python's
        # default limit for converting decimal strings to integers.
        value = 0
        for start in range(0, len(token), 9):
            chunk = token[start:start + 9]
            value = value * (10 ** len(chunk)) + int(chunk)
        return value

    for index, operation in enumerate(ops):
        parts = operation.split(" ")
        verb = parts[0]

        if (
            verb not in arities
            or len(parts) != arities[verb]
            or any(part == "" for part in parts)
        ):
            rejected.append(index)
            continue

        if verb == "undo":
            if not history:
                rejected.append(index)
                continue

            for name, old_balance, was_frozen in history.pop():
                if old_balance is None:
                    balances.pop(name, None)
                else:
                    balances[name] = old_balance

                if was_frozen:
                    frozen.add(name)
                else:
                    frozen.discard(name)
            continue

        a = parts[1]
        amount = None

        if verb in ("open", "deposit", "withdraw", "transfer"):
            amount = parse_amount(parts[-1])
            if amount is None or (verb != "open" and amount == 0):
                rejected.append(index)
                continue

        if verb == "open":
            valid = a not in balances
        elif verb == "deposit":
            valid = a in balances
        elif verb == "withdraw":
            valid = (
                a in balances
                and a not in frozen
                and balances[a] >= amount
            )
        elif verb == "transfer":
            b = parts[2]
            valid = (
                a != b
                and a in balances
                and b in balances
                and a not in frozen
                and balances[a] >= amount
            )
        elif verb == "freeze":
            valid = a in balances and a not in frozen
        else:  # unfreeze
            valid = a in balances and a in frozen

        if not valid:
            rejected.append(index)
            continue

        affected = (a, b) if verb == "transfer" else (a,)
        history.append([
            (name, balances.get(name), name in frozen)
            for name in affected
        ])

        if verb == "open":
            balances[a] = amount
        elif verb == "deposit":
            balances[a] += amount
        elif verb == "withdraw":
            balances[a] -= amount
        elif verb == "transfer":
            balances[a] -= amount
            balances[b] += amount
        elif verb == "freeze":
            frozen.add(a)
        else:
            frozen.remove(a)

    return balances, rejected
