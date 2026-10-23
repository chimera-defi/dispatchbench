def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts: dict[str, list[int | bool]] = {}
    history: list[tuple] = []
    rejected: list[int] = []

    def amount(token: str) -> int | None:
        if not token or any(c < "0" or c > "9" for c in token):
            return None
        return int(token)

    for index, operation in enumerate(ops):
        tokens = operation.split(" ")
        verb = tokens[0] if tokens else ""
        success = False

        if verb == "open" and len(tokens) == 3:
            name, raw = tokens[1], tokens[2]
            value = amount(raw)
            if value is not None and name not in accounts:
                accounts[name] = [value, False]
                history.append(("open", name))
                success = True

        elif verb == "deposit" and len(tokens) == 3:
            name, raw = tokens[1], tokens[2]
            value = amount(raw)
            if value is not None and value > 0 and name in accounts:
                accounts[name][0] += value
                history.append(("deposit", name, value))
                success = True

        elif verb == "withdraw" and len(tokens) == 3:
            name, raw = tokens[1], tokens[2]
            value = amount(raw)
            if (
                value is not None
                and value > 0
                and name in accounts
                and not accounts[name][1]
                and accounts[name][0] >= value
            ):
                accounts[name][0] -= value
                history.append(("withdraw", name, value))
                success = True

        elif verb == "transfer" and len(tokens) == 4:
            source, target, raw = tokens[1], tokens[2], tokens[3]
            value = amount(raw)
            if (
                value is not None
                and value > 0
                and source != target
                and source in accounts
                and target in accounts
                and not accounts[source][1]
                and accounts[source][0] >= value
            ):
                accounts[source][0] -= value
                accounts[target][0] += value
                history.append(("transfer", source, target, value))
                success = True

        elif verb == "freeze" and len(tokens) == 2:
            name = tokens[1]
            if name in accounts and not accounts[name][1]:
                accounts[name][1] = True
                history.append(("freeze", name))
                success = True

        elif verb == "unfreeze" and len(tokens) == 2:
            name = tokens[1]
            if name in accounts and accounts[name][1]:
                accounts[name][1] = False
                history.append(("unfreeze", name))
                success = True

        elif verb == "undo" and len(tokens) == 1:
            if history:
                action = history.pop()
                kind = action[0]

                if kind == "open":
                    del accounts[action[1]]
                elif kind == "deposit":
                    accounts[action[1]][0] -= action[2]
                elif kind == "withdraw":
                    accounts[action[1]][0] += action[2]
                elif kind == "transfer":
                    accounts[action[1]][0] += action[3]
                    accounts[action[2]][0] -= action[3]
                elif kind == "freeze":
                    accounts[action[1]][1] = False
                else:  # unfreeze
                    accounts[action[1]][1] = True

                success = True

        if not success:
            rejected.append(index)

    return {name: int(state[0]) for name, state in accounts.items()}, rejected
