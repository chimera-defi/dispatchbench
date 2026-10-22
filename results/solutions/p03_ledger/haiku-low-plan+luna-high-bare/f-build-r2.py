def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts: dict[str, tuple[int, bool]] = {}
    undo_stack: list[list[tuple[str, tuple[int, bool] | None]]] = []
    rejected: list[int] = []

    def valid_amount(text: str) -> bool:
        return bool(text) and all("0" <= ch <= "9" for ch in text)

    for i, operation in enumerate(ops):
        tokens = operation.split(" ")
        verb = tokens[0]

        if verb == "undo":
            if len(tokens) != 1 or not undo_stack:
                rejected.append(i)
                continue
            for name, previous in undo_stack.pop():
                if previous is None:
                    del accounts[name]
                else:
                    accounts[name] = previous
            continue

        record: list[tuple[str, tuple[int, bool] | None]]
        if verb == "open" and len(tokens) == 3:
            _, name, amount_text = tokens
            if not valid_amount(amount_text) or name in accounts:
                rejected.append(i)
                continue
            amount = int(amount_text)
            record = [(name, None)]
            accounts[name] = (amount, False)

        elif verb == "deposit" and len(tokens) == 3:
            _, name, amount_text = tokens
            if not valid_amount(amount_text) or name not in accounts:
                rejected.append(i)
                continue
            amount = int(amount_text)
            if amount <= 0:
                rejected.append(i)
                continue
            balance, frozen = accounts[name]
            record = [(name, accounts[name])]
            accounts[name] = (balance + amount, frozen)

        elif verb == "withdraw" and len(tokens) == 3:
            _, name, amount_text = tokens
            if not valid_amount(amount_text) or name not in accounts:
                rejected.append(i)
                continue
            amount = int(amount_text)
            balance, frozen = accounts[name]
            if amount <= 0 or frozen or balance < amount:
                rejected.append(i)
                continue
            record = [(name, accounts[name])]
            accounts[name] = (balance - amount, frozen)

        elif verb == "transfer" and len(tokens) == 4:
            _, source, target, amount_text = tokens
            if not valid_amount(amount_text):
                rejected.append(i)
                continue
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
            target_balance, target_frozen = accounts[target]
            record = [(source, accounts[source]), (target, accounts[target])]
            accounts[source] = (source_balance - amount, source_frozen)
            accounts[target] = (target_balance + amount, target_frozen)

        elif verb == "freeze" and len(tokens) == 2:
            _, name = tokens
            if name not in accounts or accounts[name][1]:
                rejected.append(i)
                continue
            record = [(name, accounts[name])]
            accounts[name] = (accounts[name][0], True)

        elif verb == "unfreeze" and len(tokens) == 2:
            _, name = tokens
            if name not in accounts or not accounts[name][1]:
                rejected.append(i)
                continue
            record = [(name, accounts[name])]
            accounts[name] = (accounts[name][0], False)

        else:
            rejected.append(i)
            continue

        undo_stack.append(record)

    return {name: balance for name, (balance, _) in accounts.items()}, rejected
