def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    balances = {}
    frozen = set()
    history = []
    rejected = []

    def parse_amount(s):
        if not s or any(c < "0" or c > "9" for c in s):
            return None
        value = 0
        for start in range(0, len(s), 9):
            chunk = s[start:start + 9]
            value = value * (10 ** len(chunk)) + int(chunk)
        return value

    def snapshot(account):
        return account, (balances[account], account in frozen)

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
            for account, previous in history.pop():
                if previous is None:
                    del balances[account]
                    frozen.discard(account)
                else:
                    balance, was_frozen = previous
                    balances[account] = balance
                    if was_frozen:
                        frozen.add(account)
                    else:
                        frozen.discard(account)
            continue

        account = tokens[1]

        if verb in ("freeze", "unfreeze"):
            if account not in balances or (
                (account in frozen) == (verb == "freeze")
            ):
                rejected.append(index)
                continue

            history.append([snapshot(account)])
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
            history.append([(account, None)])
            balances[account] = amount
            continue

        if account not in balances:
            rejected.append(index)
            continue

        if verb == "deposit":
            history.append([snapshot(account)])
            balances[account] += amount
            continue

        if account in frozen or balances[account] < amount:
            rejected.append(index)
            continue

        if verb == "withdraw":
            history.append([snapshot(account)])
            balances[account] -= amount
            continue

        destination = tokens[2]
        if destination == account or destination not in balances:
            rejected.append(index)
            continue

        history.append([snapshot(account), snapshot(destination)])
        balances[account] -= amount
        balances[destination] += amount

    return balances, rejected
