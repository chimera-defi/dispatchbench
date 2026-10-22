def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    balances: dict[str, int] = {}
    frozen: set[str] = set()
    history: list[tuple] = []
    rejected: list[int] = []

    for index, operation in enumerate(ops):
        tokens = operation.split(" ")
        verb = tokens[0] if tokens else ""

        if verb == "undo":
            if len(tokens) != 1 or not history:
                rejected.append(index)
                continue

            change = history.pop()
            kind = change[0]

            if kind == "open":
                _, account = change
                del balances[account]
                frozen.discard(account)
            elif kind in ("deposit", "withdraw"):
                _, account, amount = change
                if kind == "deposit":
                    balances[account] -= amount
                else:
                    balances[account] += amount
            elif kind == "transfer":
                _, source, destination, amount = change
                balances[source] += amount
                balances[destination] -= amount
            else:  # freeze / unfreeze
                _, account, was_frozen = change
                if was_frozen:
                    frozen.add(account)
                else:
                    frozen.discard(account)
            continue

        if verb == "open" and len(tokens) == 3:
            account, raw = tokens[1], tokens[2]
            if (account not in balances and raw.isascii() and raw.isdigit()):
                amount = int(raw)
                balances[account] = amount
                history.append(("open", account))
                continue

        elif verb == "deposit" and len(tokens) == 3:
            account, raw = tokens[1], tokens[2]
            if account in balances and raw.isascii() and raw.isdigit():
                amount = int(raw)
                if amount > 0:
                    balances[account] += amount
                    history.append(("deposit", account, amount))
                    continue

        elif verb == "withdraw" and len(tokens) == 3:
            account, raw = tokens[1], tokens[2]
            if account in balances and raw.isascii() and raw.isdigit():
                amount = int(raw)
                if amount > 0 and account not in frozen and balances[account] >= amount:
                    balances[account] -= amount
                    history.append(("withdraw", account, amount))
                    continue

        elif verb == "transfer" and len(tokens) == 4:
            source, destination, raw = tokens[1], tokens[2], tokens[3]
            if (
                source != destination
                and source in balances
                and destination in balances
                and source not in frozen
                and raw.isascii()
                and raw.isdigit()
            ):
                amount = int(raw)
                if amount > 0 and balances[source] >= amount:
                    balances[source] -= amount
                    balances[destination] += amount
                    history.append(("transfer", source, destination, amount))
                    continue

        elif verb in ("freeze", "unfreeze") and len(tokens) == 2:
            account = tokens[1]
            if account in balances:
                if verb == "freeze" and account not in frozen:
                    frozen.add(account)
                    history.append(("freeze", account, False))
                    continue
                if verb == "unfreeze" and account in frozen:
                    frozen.remove(account)
                    history.append(("unfreeze", account, True))
                    continue

        rejected.append(index)

    return balances, rejected
