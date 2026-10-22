def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    balances: dict[str, int] = {}
    frozen: set[str] = set()
    history = []
    rejected = []

    def valid_amount(token: str) -> bool:
        return bool(token) and all("0" <= ch <= "9" for ch in token)

    for index, operation in enumerate(ops):
        tokens = operation.split(" ")
        verb = tokens[0] if tokens else ""
        success = False

        if verb == "open" and len(tokens) == 3:
            name, amount = tokens[1], tokens[2]
            if valid_amount(amount) and name not in balances:
                balances[name] = int(amount)
                history.append(("open", name))
                success = True

        elif verb == "deposit" and len(tokens) == 3:
            name, amount = tokens[1], tokens[2]
            if valid_amount(amount) and int(amount) > 0 and name in balances:
                value = int(amount)
                balances[name] += value
                history.append(("balance", name, -value))
                success = True

        elif verb == "withdraw" and len(tokens) == 3:
            name, amount = tokens[1], tokens[2]
            if valid_amount(amount) and int(amount) > 0 and name in balances and name not in frozen:
                value = int(amount)
                if balances[name] >= value:
                    balances[name] -= value
                    history.append(("balance", name, value))
                    success = True

        elif verb == "transfer" and len(tokens) == 4:
            source, target, amount = tokens[1], tokens[2], tokens[3]
            if (valid_amount(amount) and int(amount) > 0 and source != target
                    and source in balances and target in balances and source not in frozen):
                value = int(amount)
                if balances[source] >= value:
                    balances[source] -= value
                    balances[target] += value
                    history.append(("transfer", source, target, value))
                    success = True

        elif verb == "freeze" and len(tokens) == 2:
            name = tokens[1]
            if name in balances and name not in frozen:
                frozen.add(name)
                history.append(("freeze", name, False))
                success = True

        elif verb == "unfreeze" and len(tokens) == 2:
            name = tokens[1]
            if name in balances and name in frozen:
                frozen.remove(name)
                history.append(("freeze", name, True))
                success = True

        elif verb == "undo" and len(tokens) == 1:
            if history:
                action = history.pop()
                kind = action[0]
                if kind == "open":
                    del balances[action[1]]
                    frozen.discard(action[1])
                elif kind == "balance":
                    _, name, delta = action
                    balances[name] += delta
                elif kind == "transfer":
                    _, source, target, value = action
                    balances[source] += value
                    balances[target] -= value
                else:
                    _, name, was_frozen = action
                    if was_frozen:
                        frozen.add(name)
                    else:
                        frozen.discard(name)
                success = True

        if not success:
            rejected.append(index)

    return balances, rejected
