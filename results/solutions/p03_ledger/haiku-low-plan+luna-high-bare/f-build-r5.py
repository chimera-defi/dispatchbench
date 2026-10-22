def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts: dict[str, list] = {}  # name -> [balance, frozen]
    undo_stack: list[tuple] = []
    rejected: list[int] = []

    for i, operation in enumerate(ops):
        tokens = operation.split(" ")
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
                accounts[record[1]][0] -= record[2]
            elif kind == "withdraw":
                accounts[record[1]][0] += record[2]
            elif kind == "transfer":
                _, source, destination, amount = record
                accounts[source][0] += amount
                accounts[destination][0] -= amount
            elif kind == "freeze":
                accounts[record[1]][1] = False
            elif kind == "unfreeze":
                accounts[record[1]][1] = True
            continue

        if verb in ("open", "deposit", "withdraw"):
            if len(tokens) != 3:
                rejected.append(i)
                continue
            name, amount_text = tokens[1], tokens[2]
            if not amount_text or any(c < "0" or c > "9" for c in amount_text):
                rejected.append(i)
                continue
            amount = int(amount_text)

            if verb == "open":
                if name in accounts:
                    rejected.append(i)
                    continue
                accounts[name] = [amount, False]
                undo_stack.append(("open", name))
            elif verb == "deposit":
                if amount <= 0 or name not in accounts:
                    rejected.append(i)
                    continue
                accounts[name][0] += amount
                undo_stack.append(("deposit", name, amount))
            else:
                if (amount <= 0 or name not in accounts
                        or accounts[name][1] or accounts[name][0] < amount):
                    rejected.append(i)
                    continue
                accounts[name][0] -= amount
                undo_stack.append(("withdraw", name, amount))

        elif verb == "transfer":
            if len(tokens) != 4:
                rejected.append(i)
                continue
            source, destination, amount_text = tokens[1], tokens[2], tokens[3]
            if not amount_text or any(c < "0" or c > "9" for c in amount_text):
                rejected.append(i)
                continue
            amount = int(amount_text)
            if (amount <= 0 or source == destination or source not in accounts
                    or destination not in accounts or accounts[source][1]
                    or accounts[source][0] < amount):
                rejected.append(i)
                continue
            accounts[source][0] -= amount
            accounts[destination][0] += amount
            undo_stack.append(("transfer", source, destination, amount))

        elif verb in ("freeze", "unfreeze"):
            if len(tokens) != 2:
                rejected.append(i)
                continue
            name = tokens[1]
            if name not in accounts:
                rejected.append(i)
                continue
            if verb == "freeze":
                if accounts[name][1]:
                    rejected.append(i)
                    continue
                accounts[name][1] = True
                undo_stack.append(("freeze", name))
            else:
                if not accounts[name][1]:
                    rejected.append(i)
                    continue
                accounts[name][1] = False
                undo_stack.append(("unfreeze", name))
        else:
            rejected.append(i)

    return {name: state[0] for name, state in accounts.items()}, rejected
