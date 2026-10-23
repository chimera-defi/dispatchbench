def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts = {}  # name -> (balance, frozen)
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
            else:
                for name, previous in history.pop():
                    if previous is None:
                        del accounts[name]
                    else:
                        accounts[name] = previous
            continue

        if verb in ("open", "deposit", "withdraw", "transfer"):
            raw = tokens[-1]
            if not all("0" <= char <= "9" for char in raw):
                rejected.append(index)
                continue

            # Parse in chunks to avoid Python's string-to-int digit limit.
            amount = 0
            for start in range(0, len(raw), 9):
                chunk = raw[start:start + 9]
                amount = amount * (10 ** len(chunk)) + int(chunk)

            if verb != "open" and amount == 0:
                rejected.append(index)
                continue

        name = tokens[1]

        if verb == "open":
            if name in accounts:
                rejected.append(index)
                continue
            history.append(((name, None),))
            accounts[name] = (amount, False)
            continue

        if name not in accounts:
            rejected.append(index)
            continue

        balance, frozen = accounts[name]

        if verb == "deposit":
            history.append(((name, accounts[name]),))
            accounts[name] = (balance + amount, frozen)

        elif verb == "withdraw":
            if frozen or balance < amount:
                rejected.append(index)
                continue
            history.append(((name, accounts[name]),))
            accounts[name] = (balance - amount, frozen)

        elif verb == "transfer":
            target = tokens[2]
            if (
                target == name
                or target not in accounts
                or frozen
                or balance < amount
            ):
                rejected.append(index)
                continue

            target_balance, target_frozen = accounts[target]
            history.append((
                (name, accounts[name]),
                (target, accounts[target]),
            ))
            accounts[name] = (balance - amount, frozen)
            accounts[target] = (target_balance + amount, target_frozen)

        elif verb == "freeze":
            if frozen:
                rejected.append(index)
                continue
            history.append(((name, accounts[name]),))
            accounts[name] = (balance, True)

        elif verb == "unfreeze":
            if not frozen:
                rejected.append(index)
                continue
            history.append(((name, accounts[name]),))
            accounts[name] = (balance, False)

    return {name: state[0] for name, state in accounts.items()}, rejected
