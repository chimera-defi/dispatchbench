def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts: dict[str, list[object]] = {}
    history: list[tuple] = []
    rejected: list[int] = []

    for i, operation in enumerate(ops):
        parts = operation.split(" ")
        verb = parts[0] if parts else ""

        if verb == "undo":
            if len(parts) != 1 or not history:
                rejected.append(i)
                continue

            record = history.pop()
            kind = record[0]

            if kind == "open":
                del accounts[record[1]]
            elif kind == "deposit":
                accounts[record[1]][0] -= record[2]
            elif kind == "withdraw":
                accounts[record[1]][0] += record[2]
            elif kind == "transfer":
                _, source, target, amount = record
                accounts[source][0] += amount
                accounts[target][0] -= amount
            elif kind == "freeze":
                accounts[record[1]][1] = False
            elif kind == "unfreeze":
                accounts[record[1]][1] = True
            continue

        valid = True
        record = None

        if verb == "open" and len(parts) == 3:
            name, amount_text = parts[1], parts[2]
            if (
                amount_text.isdecimal()
                and all("0" <= c <= "9" for c in amount_text)
                and name not in accounts
            ):
                amount = int(amount_text)
                accounts[name] = [amount, False]
                record = ("open", name)
            else:
                valid = False

        elif verb in ("deposit", "withdraw") and len(parts) == 3:
            name, amount_text = parts[1], parts[2]
            if (
                amount_text.isdecimal()
                and all("0" <= c <= "9" for c in amount_text)
                and int(amount_text) > 0
                and name in accounts
            ):
                amount = int(amount_text)
                balance, frozen = accounts[name]
                if verb == "deposit":
                    accounts[name][0] = balance + amount
                    record = ("deposit", name, amount)
                elif not frozen and balance >= amount:
                    accounts[name][0] = balance - amount
                    record = ("withdraw", name, amount)
                else:
                    valid = False
            else:
                valid = False

        elif verb == "transfer" and len(parts) == 4:
            source, target, amount_text = parts[1], parts[2], parts[3]
            if (
                amount_text.isdecimal()
                and all("0" <= c <= "9" for c in amount_text)
                and int(amount_text) > 0
                and source != target
                and source in accounts
                and target in accounts
            ):
                amount = int(amount_text)
                if not accounts[source][1] and accounts[source][0] >= amount:
                    accounts[source][0] -= amount
                    accounts[target][0] += amount
                    record = ("transfer", source, target, amount)
                else:
                    valid = False
            else:
                valid = False

        elif verb in ("freeze", "unfreeze") and len(parts) == 2:
            name = parts[1]
            if name in accounts:
                frozen = accounts[name][1]
                if verb == "freeze" and not frozen:
                    accounts[name][1] = True
                    record = ("freeze", name)
                elif verb == "unfreeze" and frozen:
                    accounts[name][1] = False
                    record = ("unfreeze", name)
                else:
                    valid = False
            else:
                valid = False

        else:
            valid = False

        if valid and record is not None:
            history.append(record)
        else:
            rejected.append(i)

    return {name: data[0] for name, data in accounts.items()}, rejected
