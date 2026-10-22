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

            action = history.pop()
            kind = action[0]

            if kind == "open":
                _, account = action
                del balances[account]
                frozen.discard(account)
            elif kind == "deposit":
                _, account, amount = action
                balances[account] -= amount
            elif kind == "withdraw":
                _, account, amount = action
                balances[account] += amount
            elif kind == "transfer":
                _, source, target, amount = action
                balances[source] += amount
                balances[target] -= amount
            elif kind in ("freeze", "unfreeze"):
                _, account = action
                if kind == "freeze":
                    frozen.discard(account)
                else:
                    frozen.add(account)
            continue

        if verb == "open" and len(tokens) == 3:
            account, raw_amount = tokens[1], tokens[2]
            if raw_amount.isascii() and raw_amount.isdigit() and account not in balances:
                balances[account] = int(raw_amount)
                history.append(("open", account))
            else:
                rejected.append(index)

        elif verb == "deposit" and len(tokens) == 3:
            account, raw_amount = tokens[1], tokens[2]
            if (raw_amount.isascii() and raw_amount.isdigit()
                    and int(raw_amount) > 0 and account in balances):
                amount = int(raw_amount)
                balances[account] += amount
                history.append(("deposit", account, amount))
            else:
                rejected.append(index)

        elif verb == "withdraw" and len(tokens) == 3:
            account, raw_amount = tokens[1], tokens[2]
            if (raw_amount.isascii() and raw_amount.isdigit()
                    and int(raw_amount) > 0 and account in balances
                    and account not in frozen
                    and balances[account] >= int(raw_amount)):
                amount = int(raw_amount)
                balances[account] -= amount
                history.append(("withdraw", account, amount))
            else:
                rejected.append(index)

        elif verb == "transfer" and len(tokens) == 4:
            source, target, raw_amount = tokens[1], tokens[2], tokens[3]
            if (raw_amount.isascii() and raw_amount.isdigit()
                    and int(raw_amount) > 0 and source != target
                    and source in balances and target in balances
                    and source not in frozen
                    and balances[source] >= int(raw_amount)):
                amount = int(raw_amount)
                balances[source] -= amount
                balances[target] += amount
                history.append(("transfer", source, target, amount))
            else:
                rejected.append(index)

        elif verb == "freeze" and len(tokens) == 2:
            account = tokens[1]
            if account in balances and account not in frozen:
                frozen.add(account)
                history.append(("freeze", account))
            else:
                rejected.append(index)

        elif verb == "unfreeze" and len(tokens) == 2:
            account = tokens[1]
            if account in balances and account in frozen:
                frozen.remove(account)
                history.append(("unfreeze", account))
            else:
                rejected.append(index)

        else:
            rejected.append(index)

    return balances, rejected
