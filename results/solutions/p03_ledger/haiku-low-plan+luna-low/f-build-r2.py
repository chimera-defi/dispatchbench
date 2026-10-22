def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts: dict[str, tuple[int, bool]] = {}
    undo_stack: list[list[tuple[str, bool, int, bool]]] = []
    rejected: list[int] = []

    for i, operation in enumerate(ops):
        tokens = operation.split(" ")
        verb = tokens[0] if tokens else ""

        expected = {
            "open": 3,
            "deposit": 3,
            "withdraw": 3,
            "transfer": 4,
            "freeze": 2,
            "unfreeze": 2,
            "undo": 1,
        }.get(verb)

        if expected is None or len(tokens) != expected:
            rejected.append(i)
            continue

        if verb == "undo":
            if not undo_stack:
                rejected.append(i)
                continue
            record = undo_stack.pop()
            for name, existed, balance, frozen in record:
                if existed:
                    accounts[name] = (balance, frozen)
                else:
                    accounts.pop(name, None)
            continue

        record: list[tuple[str, bool, int, bool]] = []

        def save(name: str) -> None:
            if name in accounts:
                balance, frozen = accounts[name]
                record.append((name, True, balance, frozen))
            else:
                record.append((name, False, 0, False))

        if verb in ("open", "deposit", "withdraw", "transfer"):
            amount_text = tokens[-1]
            if not amount_text or any(ch < "0" or ch > "9" for ch in amount_text):
                rejected.append(i)
                continue
            amount = int(amount_text)

        if verb == "open":
            name = tokens[1]
            if name in accounts:
                rejected.append(i)
                continue
            save(name)
            accounts[name] = (amount, False)

        elif verb == "deposit":
            name = tokens[1]
            if amount <= 0 or name not in accounts:
                rejected.append(i)
                continue
            balance, frozen = accounts[name]
            save(name)
            accounts[name] = (balance + amount, frozen)

        elif verb == "withdraw":
            name = tokens[1]
            if amount <= 0 or name not in accounts:
                rejected.append(i)
                continue
            balance, frozen = accounts[name]
            if frozen or balance < amount:
                rejected.append(i)
                continue
            save(name)
            accounts[name] = (balance - amount, frozen)

        elif verb == "transfer":
            source, destination = tokens[1], tokens[2]
            if (
                amount <= 0
                or source == destination
                or source not in accounts
                or destination not in accounts
            ):
                rejected.append(i)
                continue
            source_balance, source_frozen = accounts[source]
            destination_balance, destination_frozen = accounts[destination]
            if source_frozen or source_balance < amount:
                rejected.append(i)
                continue
            save(source)
            save(destination)
            accounts[source] = (source_balance - amount, source_frozen)
            accounts[destination] = (destination_balance + amount, destination_frozen)

        elif verb == "freeze":
            name = tokens[1]
            if name not in accounts or accounts[name][1]:
                rejected.append(i)
                continue
            save(name)
            balance, _ = accounts[name]
            accounts[name] = (balance, True)

        elif verb == "unfreeze":
            name = tokens[1]
            if name not in accounts or not accounts[name][1]:
                rejected.append(i)
                continue
            save(name)
            balance, _ = accounts[name]
            accounts[name] = (balance, False)

        undo_stack.append(record)

    return {name: balance for name, (balance, _) in accounts.items()}, rejected
