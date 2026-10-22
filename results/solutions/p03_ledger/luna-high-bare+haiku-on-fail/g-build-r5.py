def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    balances: dict[str, int] = {}
    frozen: set[str] = set()
    history: list[tuple] = []
    rejected: list[int] = []

    for i, op in enumerate(ops):
        tokens = op.split(" ")
        verb = tokens[0] if tokens else ""

        if verb == "undo" and len(tokens) == 1:
            if not history:
                rejected.append(i)
                continue

            action = history.pop()
            kind = action[0]

            if kind == "open":
                del balances[action[1]]
            elif kind == "deposit":
                balances[action[1]] -= action[2]
            elif kind == "withdraw":
                balances[action[1]] += action[2]
            elif kind == "transfer":
                _, source, target, amount = action
                balances[source] += amount
                balances[target] -= amount
            elif kind == "frozen":
                account, was_frozen = action[1], action[2]
                if was_frozen:
                    frozen.add(account)
                else:
                    frozen.discard(account)
            continue

        success = False

        if verb == "open" and len(tokens) == 3:
            account, amount_text = tokens[1], tokens[2]
            if amount_text and all("0" <= c <= "9" for c in amount_text):
                amount = int(amount_text)
                if account not in balances:
                    balances[account] = amount
                    history.append(("open", account))
                    success = True

        elif verb == "deposit" and len(tokens) == 3:
            account, amount_text = tokens[1], tokens[2]
            if amount_text and all("0" <= c <= "9" for c in amount_text):
                amount = int(amount_text)
                if amount > 0 and account in balances:
                    balances[account] += amount
                    history.append(("deposit", account, amount))
                    success = True

        elif verb == "withdraw" and len(tokens) == 3:
            account, amount_text = tokens[1], tokens[2]
            if amount_text and all("0" <= c <= "9" for c in amount_text):
                amount = int(amount_text)
                if (
                    amount > 0
                    and account in balances
                    and account not in frozen
                    and balances[account] >= amount
                ):
                    balances[account] -= amount
                    history.append(("withdraw", account, amount))
                    success = True

        elif verb == "transfer" and len(tokens) == 4:
            source, target, amount_text = tokens[1], tokens[2], tokens[3]
            if amount_text and all("0" <= c <= "9" for c in amount_text):
                amount = int(amount_text)
                if (
                    amount > 0
                    and source != target
                    and source in balances
                    and target in balances
                    and source not in frozen
                    and balances[source] >= amount
                ):
                    balances[source] -= amount
                    balances[target] += amount
                    history.append(("transfer", source, target, amount))
                    success = True

        elif verb in ("freeze", "unfreeze") and len(tokens) == 2:
            account = tokens[1]
            if account in balances:
                if verb == "freeze" and account not in frozen:
                    frozen.add(account)
                    history.append(("frozen", account, False))
                    success = True
                elif verb == "unfreeze" and account in frozen:
                    frozen.remove(account)
                    history.append(("frozen", account, True))
                    success = True

        if not success:
            rejected.append(i)

    return balances, rejected
