def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    balances: dict[str, int] = {}
    frozen: set[str] = set()
    history: list[tuple] = []
    rejected: list[int] = []

    for index, operation in enumerate(ops):
        tokens = operation.split(" ")
        verb = tokens[0] if tokens else ""

        if verb == "undo" and len(tokens) == 1:
            if not history:
                rejected.append(index)
                continue

            change = history.pop()
            kind = change[0]

            if kind == "open":
                _, account = change
                del balances[account]
                frozen.discard(account)
            elif kind == "balance":
                _, account, previous = change
                balances[account] = previous
            else:  # frozen state
                _, account, was_frozen = change
                if was_frozen:
                    frozen.add(account)
                else:
                    frozen.discard(account)
            continue

        change = None

        if verb == "open" and len(tokens) == 3:
            account, raw_amount = tokens[1], tokens[2]
            if (raw_amount.isascii() and raw_amount.isdigit()
                    and account not in balances):
                balances[account] = int(raw_amount)
                change = ("open", account)

        elif verb == "deposit" and len(tokens) == 3:
            account, raw_amount = tokens[1], tokens[2]
            if (raw_amount.isascii() and raw_amount.isdigit()
                    and int(raw_amount) > 0 and account in balances):
                amount = int(raw_amount)
                change = ("balance", account, balances[account])
                balances[account] += amount

        elif verb == "withdraw" and len(tokens) == 3:
            account, raw_amount = tokens[1], tokens[2]
            if (raw_amount.isascii() and raw_amount.isdigit()
                    and int(raw_amount) > 0 and account in balances
                    and account not in frozen):
                amount = int(raw_amount)
                if balances[account] >= amount:
                    change = ("balance", account, balances[account])
                    balances[account] -= amount

        elif verb == "transfer" and len(tokens) == 4:
            source, target, raw_amount = tokens[1], tokens[2], tokens[3]
            if (raw_amount.isascii() and raw_amount.isdigit()
                    and int(raw_amount) > 0 and source != target
                    and source in balances and target in balances
                    and source not in frozen):
                amount = int(raw_amount)
                if balances[source] >= amount:
                    change = ("balance", source, balances[source],
                              target, balances[target])
                    balances[source] -= amount
                    balances[target] += amount

        elif verb == "freeze" and len(tokens) == 2:
            account = tokens[1]
            if account in balances and account not in frozen:
                change = ("frozen", account, False)
                frozen.add(account)

        elif verb == "unfreeze" and len(tokens) == 2:
            account = tokens[1]
            if account in balances and account in frozen:
                change = ("frozen", account, True)
                frozen.remove(account)

        if change is None:
            rejected.append(index)
        else:
            history.append(change)

    return balances, rejected
