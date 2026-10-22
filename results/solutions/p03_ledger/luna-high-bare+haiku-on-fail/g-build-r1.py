def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    balances: dict[str, int] = {}
    frozen: set[str] = set()
    history: list[tuple] = []
    rejected: list[int] = []

    for i, operation in enumerate(ops):
        parts = operation.split(" ")
        if not parts or any(part == "" for part in parts):
            rejected.append(i)
            continue

        verb = parts[0]

        if verb == "undo":
            if len(parts) != 1 or not history:
                rejected.append(i)
                continue

            action = history.pop()
            kind = action[0]

            if kind == "open":
                del balances[action[1]]
                frozen.discard(action[1])
            elif kind == "deposit":
                balances[action[1]] -= action[2]
            elif kind == "withdraw":
                balances[action[1]] += action[2]
            elif kind == "transfer":
                _, source, target, amount = action
                balances[source] += amount
                balances[target] -= amount
            else:  # freeze or unfreeze
                _, account, was_frozen = action
                if was_frozen:
                    frozen.add(account)
                else:
                    frozen.discard(account)
            continue

        if verb == "open" and len(parts) == 3:
            account, raw_amount = parts[1], parts[2]
            if (raw_amount.isascii() and raw_amount.isdigit()
                    and account not in balances):
                balances[account] = int(raw_amount)
                history.append(("open", account))
                continue

        elif verb == "deposit" and len(parts) == 3:
            account, raw_amount = parts[1], parts[2]
            if raw_amount.isascii() and raw_amount.isdigit():
                amount = int(raw_amount)
                if amount > 0 and account in balances:
                    balances[account] += amount
                    history.append(("deposit", account, amount))
                    continue

        elif verb == "withdraw" and len(parts) == 3:
            account, raw_amount = parts[1], parts[2]
            if raw_amount.isascii() and raw_amount.isdigit():
                amount = int(raw_amount)
                if (amount > 0 and account in balances and account not in frozen
                        and balances[account] >= amount):
                    balances[account] -= amount
                    history.append(("withdraw", account, amount))
                    continue

        elif verb == "transfer" and len(parts) == 4:
            source, target, raw_amount = parts[1], parts[2], parts[3]
            if raw_amount.isascii() and raw_amount.isdigit():
                amount = int(raw_amount)
                if (amount > 0 and source != target and source in balances
                        and target in balances and source not in frozen
                        and balances[source] >= amount):
                    balances[source] -= amount
                    balances[target] += amount
                    history.append(("transfer", source, target, amount))
                    continue

        elif verb == "freeze" and len(parts) == 2:
            account = parts[1]
            if account in balances and account not in frozen:
                frozen.add(account)
                history.append(("freeze", account, False))
                continue

        elif verb == "unfreeze" and len(parts) == 2:
            account = parts[1]
            if account in balances and account in frozen:
                frozen.remove(account)
                history.append(("unfreeze", account, True))
                continue

        rejected.append(i)

    return balances, rejected
