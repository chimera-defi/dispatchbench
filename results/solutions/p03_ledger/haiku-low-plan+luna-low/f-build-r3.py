def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts: dict[str, tuple[int, bool]] = {}
    undo_stack: list[tuple] = []
    rejected: list[int] = []

    def valid_amount(token: str) -> bool:
        return bool(token) and all("0" <= ch <= "9" for ch in token)

    for i, operation in enumerate(ops):
        tokens = operation.split(" ")
        verb = tokens[0] if tokens else ""

        if verb == "undo":
            if len(tokens) != 1 or not undo_stack:
                rejected.append(i)
                continue

            record = undo_stack.pop()
            kind = record[0]

            if kind == "open":
                del accounts[record[1]]
            elif kind == "deposit":
                name, amount = record[1], record[2]
                balance, frozen = accounts[name]
                accounts[name] = (balance - amount, frozen)
            elif kind == "withdraw":
                name, amount = record[1], record[2]
                balance, frozen = accounts[name]
                accounts[name] = (balance + amount, frozen)
            elif kind == "transfer":
                source, target, amount = record[1], record[2], record[3]
                source_balance, source_frozen = accounts[source]
                target_balance, target_frozen = accounts[target]
                accounts[source] = (source_balance + amount, source_frozen)
                accounts[target] = (target_balance - amount, target_frozen)
            elif kind == "freeze":
                name = record[1]
                balance, _ = accounts[name]
                accounts[name] = (balance, False)
            elif kind == "unfreeze":
                name = record[1]
                balance, _ = accounts[name]
                accounts[name] = (balance, True)
            continue

        if verb == "open":
            if len(tokens) != 3 or not valid_amount(tokens[2]):
                rejected.append(i)
                continue
            name, amount_token = tokens[1], tokens[2]
            try:
                amount = int(amount_token)
            except ValueError:
                rejected.append(i)
                continue
            if name in accounts:
                rejected.append(i)
                continue
            accounts[name] = (amount, False)
            undo_stack.append(("open", name))

        elif verb == "deposit":
            if len(tokens) != 3 or not valid_amount(tokens[2]):
                rejected.append(i)
                continue
            name, amount_token = tokens[1], tokens[2]
            try:
                amount = int(amount_token)
            except ValueError:
                rejected.append(i)
                continue
            if amount <= 0 or name not in accounts:
                rejected.append(i)
                continue
            balance, frozen = accounts[name]
            accounts[name] = (balance + amount, frozen)
            undo_stack.append(("deposit", name, amount))

        elif verb == "withdraw":
            if len(tokens) != 3 or not valid_amount(tokens[2]):
                rejected.append(i)
                continue
            name, amount_token = tokens[1], tokens[2]
            try:
                amount = int(amount_token)
            except ValueError:
                rejected.append(i)
                continue
            if amount <= 0 or name not in accounts:
                rejected.append(i)
                continue
            balance, frozen = accounts[name]
            if frozen or balance < amount:
                rejected.append(i)
                continue
            accounts[name] = (balance - amount, frozen)
            undo_stack.append(("withdraw", name, amount))

        elif verb == "transfer":
            if len(tokens) != 4 or not valid_amount(tokens[3]):
                rejected.append(i)
                continue
            source, target, amount_token = tokens[1], tokens[2], tokens[3]
            try:
                amount = int(amount_token)
            except ValueError:
                rejected.append(i)
                continue
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
            target_balance, target_frozen = accounts[target]
            accounts[source] = (source_balance - amount, source_frozen)
            accounts[target] = (target_balance + amount, target_frozen)
            undo_stack.append(("transfer", source, target, amount))

        elif verb in ("freeze", "unfreeze"):
            if len(tokens) != 2:
                rejected.append(i)
                continue
            name = tokens[1]
            if name not in accounts:
                rejected.append(i)
                continue
            balance, frozen = accounts[name]
            if (verb == "freeze" and frozen) or (verb == "unfreeze" and not frozen):
                rejected.append(i)
                continue
            accounts[name] = (balance, verb == "freeze")
            undo_stack.append((verb, name))

        else:
            rejected.append(i)

    balances = {name: balance for name, (balance, _) in accounts.items()}
    return balances, rejected
