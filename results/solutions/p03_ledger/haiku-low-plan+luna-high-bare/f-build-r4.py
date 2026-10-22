def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts: dict[str, tuple[int, bool]] = {}
    history: list[list[tuple[str, tuple[int, bool] | None]]] = []
    rejected: list[int] = []

    def parse_amount(token: str) -> int | None:
        if not token or any(ch < "0" or ch > "9" for ch in token):
            return None
        return int(token)

    for i, operation in enumerate(ops):
        tokens = operation.split(" ")
        if not tokens or any(token == "" for token in tokens):
            rejected.append(i)
            continue

        verb = tokens[0]

        if verb == "undo":
            if len(tokens) != 1 or not history:
                rejected.append(i)
                continue
            record = history.pop()
            for name, prior_state in record:
                if prior_state is None:
                    accounts.pop(name, None)
                else:
                    accounts[name] = prior_state
            continue

        record: list[tuple[str, tuple[int, bool] | None]]
        if verb == "open":
            if len(tokens) != 3:
                rejected.append(i)
                continue
            name = tokens[1]
            amount = parse_amount(tokens[2])
            if amount is None or name in accounts:
                rejected.append(i)
                continue
            record = [(name, None)]
            accounts[name] = (amount, False)

        elif verb in ("deposit", "withdraw"):
            if len(tokens) != 3:
                rejected.append(i)
                continue
            name = tokens[1]
            amount = parse_amount(tokens[2])
            if amount is None or amount <= 0 or name not in accounts:
                rejected.append(i)
                continue
            balance, frozen = accounts[name]
            if verb == "withdraw" and (frozen or balance < amount):
                rejected.append(i)
                continue
            record = [(name, accounts[name])]
            accounts[name] = (
                balance + amount if verb == "deposit" else balance - amount,
                frozen,
            )

        elif verb == "transfer":
            if len(tokens) != 4:
                rejected.append(i)
                continue
            source, target = tokens[1], tokens[2]
            amount = parse_amount(tokens[3])
            if (
                amount is None
                or amount <= 0
                or source == target
                or source not in accounts
                or target not in accounts
            ):
                rejected.append(i)
                continue
            source_balance, source_frozen = accounts[source]
            target_balance, target_frozen = accounts[target]
            if source_frozen or source_balance < amount:
                rejected.append(i)
                continue
            record = [(source, accounts[source]), (target, accounts[target])]
            accounts[source] = (source_balance - amount, source_frozen)
            accounts[target] = (target_balance + amount, target_frozen)

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
            record = [(name, accounts[name])]
            accounts[name] = (balance, verb == "freeze")

        else:
            rejected.append(i)
            continue

        history.append(record)

    return {name: balance for name, (balance, _) in accounts.items()}, rejected
