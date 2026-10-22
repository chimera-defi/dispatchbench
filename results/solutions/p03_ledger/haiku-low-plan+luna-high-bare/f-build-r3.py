def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts: dict[str, list] = {}
    undo_stack: list[tuple] = []
    rejected: list[int] = []

    def parse_amount(s: str):
        if not s or any(ch < "0" or ch > "9" for ch in s):
            return None

        # Convert in small chunks to support digit strings beyond Python's
        # built-in decimal-to-int conversion limit.
        value = 0
        first = len(s) % 9
        pos = 0
        if first:
            chunk = s[:first]
            value = int(chunk)
            pos = first
        while pos < len(s):
            value = value * 1_000_000_000 + int(s[pos:pos + 9])
            pos += 9
        return value

    for i, operation in enumerate(ops):
        parts = operation.split(" ")
        verb = parts[0]

        if verb == "undo":
            if len(parts) != 1 or not undo_stack:
                rejected.append(i)
                continue

            record = undo_stack.pop()
            kind = record[0]

            if kind == "open":
                accounts.pop(record[1])
            elif kind == "deposit":
                accounts[record[1]][0] -= record[2]
            elif kind == "withdraw":
                accounts[record[1]][0] += record[2]
            elif kind == "transfer":
                _, source, target, amount = record
                accounts[source][0] += amount
                accounts[target][0] -= amount
            elif kind == "frozen":
                accounts[record[1]][1] = record[2]
            continue

        if verb == "open" and len(parts) == 3:
            _, name, amount_s = parts
            amount = parse_amount(amount_s)
            if not name or amount is None or name in accounts:
                rejected.append(i)
                continue
            accounts[name] = [amount, False]
            undo_stack.append(("open", name))

        elif verb == "deposit" and len(parts) == 3:
            _, name, amount_s = parts
            amount = parse_amount(amount_s)
            if not name or amount is None or amount == 0 or name not in accounts:
                rejected.append(i)
                continue
            accounts[name][0] += amount
            undo_stack.append(("deposit", name, amount))

        elif verb == "withdraw" and len(parts) == 3:
            _, name, amount_s = parts
            amount = parse_amount(amount_s)
            if (
                not name
                or amount is None
                or amount == 0
                or name not in accounts
                or accounts[name][1]
                or accounts[name][0] < amount
            ):
                rejected.append(i)
                continue
            accounts[name][0] -= amount
            undo_stack.append(("withdraw", name, amount))

        elif verb == "transfer" and len(parts) == 4:
            _, source, target, amount_s = parts
            amount = parse_amount(amount_s)
            if (
                not source
                or not target
                or amount is None
                or amount == 0
                or source == target
                or source not in accounts
                or target not in accounts
                or accounts[source][1]
                or accounts[source][0] < amount
            ):
                rejected.append(i)
                continue
            accounts[source][0] -= amount
            accounts[target][0] += amount
            undo_stack.append(("transfer", source, target, amount))

        elif verb == "freeze" and len(parts) == 2:
            _, name = parts
            if not name or name not in accounts or accounts[name][1]:
                rejected.append(i)
                continue
            accounts[name][1] = True
            undo_stack.append(("frozen", name, False))

        elif verb == "unfreeze" and len(parts) == 2:
            _, name = parts
            if not name or name not in accounts or not accounts[name][1]:
                rejected.append(i)
                continue
            accounts[name][1] = False
            undo_stack.append(("frozen", name, True))

        else:
            rejected.append(i)

    balances = {name: state[0] for name, state in accounts.items()}
    return balances, rejected
