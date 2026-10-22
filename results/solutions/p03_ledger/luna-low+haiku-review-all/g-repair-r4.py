def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts = {}  # name -> [balance, frozen]
    history = []
    rejected = []

    def parse_amount(raw: str) -> int | None:
        if raw.isascii() and raw.isdigit():
            return int(raw)
        return None

    for index, operation in enumerate(ops):
        tokens = operation.split(" ")
        verb = tokens[0]

        if verb == "undo":
            if len(tokens) != 1 or not history:
                rejected.append(index)
                continue

            action = history.pop()
            kind = action[0]

            if kind == "open":
                del accounts[action[1]]
            elif kind == "balance":
                accounts[action[1]][0] = action[2]
            elif kind == "transfer":
                _, source, source_balance, target, target_balance = action
                accounts[source][0] = source_balance
                accounts[target][0] = target_balance
            else:  # freeze state
                accounts[action[1]][1] = action[2]
            continue

        if verb == "open":
            if len(tokens) != 3:
                rejected.append(index)
                continue
            _, name, raw_amount = tokens
            amount = parse_amount(raw_amount)
            if amount is None or name in accounts:
                rejected.append(index)
                continue
            accounts[name] = [amount, False]
            history.append(("open", name))
            continue

        if verb == "deposit" or verb == "withdraw":
            if len(tokens) != 3:
                rejected.append(index)
                continue
            _, name, raw_amount = tokens
            amount = parse_amount(raw_amount)
            if amount is None or amount <= 0 or name not in accounts:
                rejected.append(index)
                continue

            balance, frozen = accounts[name]
            if verb == "deposit":
                accounts[name][0] = balance + amount
                history.append(("balance", name, balance))
            elif frozen or balance < amount:
                rejected.append(index)
            else:
                accounts[name][0] = balance - amount
                history.append(("balance", name, balance))
            continue

        if verb == "transfer":
            if len(tokens) != 4:
                rejected.append(index)
                continue
            _, source, target, raw_amount = tokens
            amount = parse_amount(raw_amount)
            if (amount is None or amount <= 0 or source == target
                    or source not in accounts or target not in accounts):
                rejected.append(index)
                continue

            source_balance, source_frozen = accounts[source]
            if source_frozen or source_balance < amount:
                rejected.append(index)
                continue

            target_balance = accounts[target][0]
            accounts[source][0] = source_balance - amount
            accounts[target][0] = target_balance + amount
            history.append(("transfer", source, source_balance, target, target_balance))
            continue

        if verb in ("freeze", "unfreeze"):
            if len(tokens) != 2:
                rejected.append(index)
                continue
            _, name = tokens
            if name not in accounts:
                rejected.append(index)
                continue

            was_frozen = accounts[name][1]
            if (verb == "freeze" and was_frozen) or (verb == "unfreeze" and not was_frozen):
                rejected.append(index)
                continue

            accounts[name][1] = verb == "freeze"
            history.append(("state", name, was_frozen))
            continue

        rejected.append(index)

    return ({name: data[0] for name, data in accounts.items()}, rejected)
