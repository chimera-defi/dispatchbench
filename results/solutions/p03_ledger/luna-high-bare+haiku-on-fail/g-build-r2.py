def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    balances: dict[str, int] = {}
    frozen: set[str] = set()
    history: list[tuple] = []
    rejected: list[int] = []

    def parse_amount(token: str) -> int | None:
        if not token or any(ch < "0" or ch > "9" for ch in token):
            return None
        return int(token)

    for i, operation in enumerate(ops):
        parts = operation.split()
        if not parts:
            rejected.append(i)
            continue

        verb = parts[0]

        if verb == "undo":
            if len(parts) != 1 or not history:
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
            elif kind == "freeze":
                frozen.remove(action[1])
            elif kind == "unfreeze":
                frozen.add(action[1])
            continue

        if verb == "open" and len(parts) == 3:
            name = parts[1]
            amount = parse_amount(parts[2])
            if amount is None or name in balances:
                rejected.append(i)
                continue
            balances[name] = amount
            history.append(("open", name))

        elif verb == "deposit" and len(parts) == 3:
            name = parts[1]
            amount = parse_amount(parts[2])
            if amount is None or amount <= 0 or name not in balances:
                rejected.append(i)
                continue
            balances[name] += amount
            history.append(("deposit", name, amount))

        elif verb == "withdraw" and len(parts) == 3:
            name = parts[1]
            amount = parse_amount(parts[2])
            if (amount is None or amount <= 0 or name not in balances
                    or name in frozen or balances[name] < amount):
                rejected.append(i)
                continue
            balances[name] -= amount
            history.append(("withdraw", name, amount))

        elif verb == "transfer" and len(parts) == 4:
            source, target = parts[1], parts[2]
            amount = parse_amount(parts[3])
            if (amount is None or amount <= 0 or source == target
                    or source not in balances or target not in balances
                    or source in frozen or balances[source] < amount):
                rejected.append(i)
                continue
            balances[source] -= amount
            balances[target] += amount
            history.append(("transfer", source, target, amount))

        elif verb == "freeze" and len(parts) == 2:
            name = parts[1]
            if name not in balances or name in frozen:
                rejected.append(i)
                continue
            frozen.add(name)
            history.append(("freeze", name))

        elif verb == "unfreeze" and len(parts) == 2:
            name = parts[1]
            if name not in balances or name not in frozen:
                rejected.append(i)
                continue
            frozen.remove(name)
            history.append(("unfreeze", name))

        else:
            rejected.append(i)

    return balances, rejected
