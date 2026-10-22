def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts: dict[str, list] = {}
    history = []
    rejected = []

    def valid_amount(token: str) -> bool:
        return bool(token) and all("0" <= ch <= "9" for ch in token)

    for i, operation in enumerate(ops):
        parts = operation.split(" ")
        verb = parts[0]

        if verb == "undo":
            if len(parts) != 1 or not history:
                rejected.append(i)
                continue

            record = history.pop()
            for name, previous in record:
                if previous is None:
                    accounts.pop(name, None)
                else:
                    accounts[name] = previous
            continue

        if verb == "open":
            if len(parts) != 3 or not valid_amount(parts[2]):
                rejected.append(i)
                continue
            name, amount_text = parts[1], parts[2]
            amount = int(amount_text)
            if name in accounts:
                rejected.append(i)
                continue
            accounts[name] = [amount, False]
            history.append([(name, None)])
            continue

        if verb in ("deposit", "withdraw"):
            if len(parts) != 3 or not valid_amount(parts[2]):
                rejected.append(i)
                continue
            name, amount_text = parts[1], parts[2]
            amount = int(amount_text)
            if amount <= 0 or name not in accounts:
                rejected.append(i)
                continue

            balance, frozen = accounts[name]
            if verb == "withdraw" and (frozen or balance < amount):
                rejected.append(i)
                continue

            history.append([(name, accounts[name][:])])
            accounts[name][0] += amount if verb == "deposit" else -amount
            continue

        if verb == "transfer":
            if len(parts) != 4 or not valid_amount(parts[3]):
                rejected.append(i)
                continue
            source, target, amount_text = parts[1], parts[2], parts[3]
            amount = int(amount_text)
            if (
                amount <= 0
                or source == target
                or source not in accounts
                or target not in accounts
            ):
                rejected.append(i)
                continue

            source_balance, source_frozen = accounts[source]
            if source_frozen or source_balance < amount:
                rejected.append(i)
                continue

            history.append([
                (source, accounts[source][:]),
                (target, accounts[target][:]),
            ])
            accounts[source][0] -= amount
            accounts[target][0] += amount
            continue

        if verb in ("freeze", "unfreeze"):
            if len(parts) != 2:
                rejected.append(i)
                continue
            name = parts[1]
            if name not in accounts:
                rejected.append(i)
                continue

            _, frozen = accounts[name]
            if (verb == "freeze" and frozen) or (verb == "unfreeze" and not frozen):
                rejected.append(i)
                continue

            history.append([(name, accounts[name][:])])
            accounts[name][1] = verb == "freeze"
            continue

        rejected.append(i)

    return {name: state[0] for name, state in accounts.items()}, rejected
