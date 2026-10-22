def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts: dict[str, tuple[int, bool]] = {}
    undo_stack: list[tuple] = []
    rejected: list[int] = []

    def valid_amount(s: str) -> bool:
        return bool(s) and all("0" <= ch <= "9" for ch in s)

    for i, op in enumerate(ops):
        tokens = op.split(" ")
        verb = tokens[0]

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
                source, destination, amount = record[1:]
                source_balance, source_frozen = accounts[source]
                dest_balance, dest_frozen = accounts[destination]
                accounts[source] = (source_balance + amount, source_frozen)
                accounts[destination] = (dest_balance - amount, dest_frozen)
            elif kind == "freeze":
                name = record[1]
                balance, _ = accounts[name]
                accounts[name] = (balance, False)
            elif kind == "unfreeze":
                name = record[1]
                balance, _ = accounts[name]
                accounts[name] = (balance, True)
            continue

        record = None

        if verb == "open" and len(tokens) == 3:
            name, amount_s = tokens[1], tokens[2]
            if valid_amount(amount_s) and name not in accounts:
                accounts[name] = (int(amount_s), False)
                record = ("open", name)

        elif verb == "deposit" and len(tokens) == 3:
            name, amount_s = tokens[1], tokens[2]
            if valid_amount(amount_s):
                amount = int(amount_s)
                if amount > 0 and name in accounts:
                    balance, frozen = accounts[name]
                    accounts[name] = (balance + amount, frozen)
                    record = ("deposit", name, amount)

        elif verb == "withdraw" and len(tokens) == 3:
            name, amount_s = tokens[1], tokens[2]
            if valid_amount(amount_s):
                amount = int(amount_s)
                if amount > 0 and name in accounts:
                    balance, frozen = accounts[name]
                    if not frozen and balance >= amount:
                        accounts[name] = (balance - amount, frozen)
                        record = ("withdraw", name, amount)

        elif verb == "transfer" and len(tokens) == 4:
            source, destination, amount_s = tokens[1], tokens[2], tokens[3]
            if valid_amount(amount_s):
                amount = int(amount_s)
                if (
                    amount > 0
                    and source != destination
                    and source in accounts
                    and destination in accounts
                ):
                    source_balance, source_frozen = accounts[source]
                    if not source_frozen and source_balance >= amount:
                        dest_balance, dest_frozen = accounts[destination]
                        accounts[source] = (source_balance - amount, source_frozen)
                        accounts[destination] = (dest_balance + amount, dest_frozen)
                        record = ("transfer", source, destination, amount)

        elif verb == "freeze" and len(tokens) == 2:
            name = tokens[1]
            if name in accounts:
                balance, frozen = accounts[name]
                if not frozen:
                    accounts[name] = (balance, True)
                    record = ("freeze", name)

        elif verb == "unfreeze" and len(tokens) == 2:
            name = tokens[1]
            if name in accounts:
                balance, frozen = accounts[name]
                if frozen:
                    accounts[name] = (balance, False)
                    record = ("unfreeze", name)

        if record is None:
            rejected.append(i)
        else:
            undo_stack.append(record)

    return ({name: balance for name, (balance, _) in accounts.items()}, rejected)
