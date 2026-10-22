def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts: dict[str, int] = {}
    frozen: set[str] = set()
    # Each history entry is a callable that reverts one successful op.
    history: list[tuple] = []
    rejected: list[int] = []

    def valid_amount(s: str) -> bool:
        return s.isascii() and s.isdigit()

    for i, op in enumerate(ops):
        tokens = op.split(" ")
        if not tokens or tokens[0] == "":
            rejected.append(i)
            continue
        verb = tokens[0]
        args = tokens[1:]

        if verb == "open" and len(args) == 2:
            name, amt = args
            if not valid_amount(amt) or name in accounts:
                rejected.append(i)
                continue
            n = int(amt)
            accounts[name] = n
            history.append(("open", name))

        elif verb == "deposit" and len(args) == 2:
            name, amt = args
            if not valid_amount(amt) or name not in accounts:
                rejected.append(i)
                continue
            n = int(amt)
            if n <= 0:
                rejected.append(i)
                continue
            accounts[name] += n
            history.append(("deposit", name, n))

        elif verb == "withdraw" and len(args) == 2:
            name, amt = args
            if not valid_amount(amt) or name not in accounts or name in frozen:
                rejected.append(i)
                continue
            n = int(amt)
            if n <= 0 or accounts[name] < n:
                rejected.append(i)
                continue
            accounts[name] -= n
            history.append(("withdraw", name, n))

        elif verb == "transfer" and len(args) == 3:
            src, dst, amt = args
            if (not valid_amount(amt) or src not in accounts or dst not in accounts
                    or src == dst or src in frozen):
                rejected.append(i)
                continue
            n = int(amt)
            if n <= 0 or accounts[src] < n:
                rejected.append(i)
                continue
            accounts[src] -= n
            accounts[dst] += n
            history.append(("transfer", src, dst, n))

        elif verb == "freeze" and len(args) == 1:
            name = args[0]
            if name not in accounts or name in frozen:
                rejected.append(i)
                continue
            frozen.add(name)
            history.append(("freeze", name))

        elif verb == "unfreeze" and len(args) == 1:
            name = args[0]
            if name not in accounts or name not in frozen:
                rejected.append(i)
                continue
            frozen.discard(name)
            history.append(("unfreeze", name))

        elif verb == "undo" and len(args) == 0:
            if not history:
                rejected.append(i)
                continue
            entry = history.pop()
            kind = entry[0]
            if kind == "open":
                del accounts[entry[1]]
                frozen.discard(entry[1])
            elif kind == "deposit":
                accounts[entry[1]] -= entry[2]
            elif kind == "withdraw":
                accounts[entry[1]] += entry[2]
            elif kind == "transfer":
                accounts[entry[1]] += entry[3]
                accounts[entry[2]] -= entry[3]
            elif kind == "freeze":
                frozen.discard(entry[1])
            elif kind == "unfreeze":
                frozen.add(entry[1])

        else:
            rejected.append(i)

    return accounts, rejected
