def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts = {}
    history = []
    rejected = []

    for index, operation in enumerate(ops):
        parts = operation.split(" ")
        verb = parts[0] if parts else ""
        success = False

        if verb == "open" and len(parts) == 3:
            _, name, amount_text = parts
            if amount_text.isdigit() and all("0" <= ch <= "9" for ch in amount_text):
                amount = int(amount_text)
                if name not in accounts:
                    accounts[name] = [amount, False]
                    history.append(("open", name, amount))
                    success = True

        elif verb == "deposit" and len(parts) == 3:
            _, name, amount_text = parts
            if amount_text.isdigit() and all("0" <= ch <= "9" for ch in amount_text):
                amount = int(amount_text)
                if amount > 0 and name in accounts:
                    accounts[name][0] += amount
                    history.append(("deposit", name, amount))
                    success = True

        elif verb == "withdraw" and len(parts) == 3:
            _, name, amount_text = parts
            if amount_text.isdigit() and all("0" <= ch <= "9" for ch in amount_text):
                amount = int(amount_text)
                if amount > 0 and name in accounts:
                    balance, frozen = accounts[name]
                    if not frozen and balance >= amount:
                        accounts[name][0] -= amount
                        history.append(("withdraw", name, amount))
                        success = True

        elif verb == "transfer" and len(parts) == 4:
            _, source, target, amount_text = parts
            if amount_text.isdigit() and all("0" <= ch <= "9" for ch in amount_text):
                amount = int(amount_text)
                if (
                    amount > 0
                    and source != target
                    and source in accounts
                    and target in accounts
                ):
                    balance, frozen = accounts[source]
                    if not frozen and balance >= amount:
                        accounts[source][0] -= amount
                        accounts[target][0] += amount
                        history.append(("transfer", source, target, amount))
                        success = True

        elif verb == "freeze" and len(parts) == 2:
            _, name = parts
            if name in accounts and not accounts[name][1]:
                accounts[name][1] = True
                history.append(("freeze", name))
                success = True

        elif verb == "unfreeze" and len(parts) == 2:
            _, name = parts
            if name in accounts and accounts[name][1]:
                accounts[name][1] = False
                history.append(("unfreeze", name))
                success = True

        elif verb == "undo" and len(parts) == 1:
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
                    source, target, amount = action[1:]
                    accounts[source][0] += amount
                    accounts[target][0] -= amount
                elif kind == "freeze":
                    accounts[action[1]][1] = False
                elif kind == "unfreeze":
                    accounts[action[1]][1] = True
                success = True

        if not success:
            rejected.append(index)

    return {name: state[0] for name, state in accounts.items()}, rejected
