def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts = {}
    history = []
    rejected = []

    def valid_amount(token):
        return bool(token) and all('0' <= ch <= '9' for ch in token)

    for i, op in enumerate(ops):
        parts = op.split(' ')
        verb = parts[0] if parts else ''

        if verb == 'undo':
            if len(parts) != 1 or not history:
                rejected.append(i)
                continue

            action = history.pop()
            if action[0] == 'remove':
                del accounts[action[1]]
            elif action[0] == 'add':
                _, name, delta = action
                accounts[name] += delta
            else:  # set_frozen
                _, name, previous = action
                accounts[name][1] = previous
            continue

        if verb == 'open':
            if len(parts) != 3 or not valid_amount(parts[2]):
                rejected.append(i)
                continue
            name, amount = parts[1], int(parts[2])
            if name in accounts:
                rejected.append(i)
                continue
            accounts[name] = [amount, False]
            history.append(('remove', name))

        elif verb == 'deposit':
            if len(parts) != 3 or not valid_amount(parts[2]):
                rejected.append(i)
                continue
            name, amount = parts[1], int(parts[2])
            if amount <= 0 or name not in accounts:
                rejected.append(i)
                continue
            accounts[name][0] += amount
            history.append(('add', name, -amount))

        elif verb == 'withdraw':
            if len(parts) != 3 or not valid_amount(parts[2]):
                rejected.append(i)
                continue
            name, amount = parts[1], int(parts[2])
            if (amount <= 0 or name not in accounts or
                    accounts[name][1] or accounts[name][0] < amount):
                rejected.append(i)
                continue
            accounts[name][0] -= amount
            history.append(('add', name, amount))

        elif verb == 'transfer':
            if len(parts) != 4 or not valid_amount(parts[3]):
                rejected.append(i)
                continue
            source, target, amount = parts[1], parts[2], int(parts[3])
            if (amount <= 0 or source == target or source not in accounts or
                    target not in accounts or accounts[source][1] or
                    accounts[source][0] < amount):
                rejected.append(i)
                continue
            accounts[source][0] -= amount
            accounts[target][0] += amount
            history.append(('transfer', source, target, amount))

        elif verb == 'freeze':
            if len(parts) != 2 or parts[1] not in accounts or accounts[parts[1]][1]:
                rejected.append(i)
                continue
            name = parts[1]
            accounts[name][1] = True
            history.append(('set_frozen', name, False))

        elif verb == 'unfreeze':
            if len(parts) != 2 or parts[1] not in accounts or not accounts[parts[1]][1]:
                rejected.append(i)
                continue
            name = parts[1]
            accounts[name][1] = False
            history.append(('set_frozen', name, True))

        else:
            rejected.append(i)
            continue

    balances = {name: state[0] for name, state in accounts.items()}
    return balances, rejected
