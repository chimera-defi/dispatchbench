def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts: dict[str, list] = {}
    history: list[tuple] = []
    rejected: list[int] = []

    def parse_amount(token: str):
        if not token or any(ch < "0" or ch > "9" for ch in token):
            return None
        return int(token)

    for i, op in enumerate(ops):
        parts = op.split(" ")
        verb = parts[0] if parts else ""

        if verb == "undo" and len(parts) == 1:
            if not history:
                rejected.append(i)
                continue
            action = history.pop()
            if action[0] == "remove":
                del accounts[action[1]]
            elif action[0] == "add":
                accounts[action[1]][0] += action[2]
            elif action[0] == "transfer":
                accounts[action[1]][0] += action[2]
                accounts[action[3]][0] += action[4]
            else:
                accounts[action[1]][1] = action[2]
            continue

        record = None

        if verb == "open" and len(parts) == 3:
            name = parts[1]
            amount = parse_amount(parts[2])
            if name and amount is not None and name not in accounts:
                accounts[name] = [amount, False]
                record = ("remove", name)

        elif verb in ("deposit", "withdraw") and len(parts) == 3:
            name = parts[1]
            amount = parse_amount(parts[2])
            if name and amount is not None and amount > 0 and name in accounts:
                balance, frozen = accounts[name]
                if verb == "deposit":
                    accounts[name][0] += amount
                    record = ("add", name, -amount)
                elif not frozen and balance >= amount:
                    accounts[name][0] -= amount
                    record = ("add", name, amount)

        elif verb == "transfer" and len(parts) == 4:
            source, target = parts[1], parts[2]
            amount = parse_amount(parts[3])
            if (
                source and target and amount is not None and amount > 0
                and source != target and source in accounts and target in accounts
                and not accounts[source][1] and accounts[source][0] >= amount
            ):
                accounts[source][0] -= amount
                accounts[target][0] += amount
                record = ("transfer", source, amount, target, -amount)

        elif verb in ("freeze", "unfreeze") and len(parts) == 2:
            name = parts[1]
            if name and name in accounts:
                was_frozen = accounts[name][1]
                if (verb == "freeze" and not was_frozen) or (
                    verb == "unfreeze" and was_frozen
                ):
                    accounts[name][1] = verb == "freeze"
                    record = ("frozen", name, was_frozen)

        if record is None:
            rejected.append(i)
        else:
            history.append(record)

    return ({name: account[0] for name, account in accounts.items()}, rejected)
