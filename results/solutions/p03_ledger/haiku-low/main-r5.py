def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    accounts: dict[str, dict] = {}  # name -> {"balance": int, "frozen": bool}
    history: list = []  # stack of undo records for successful non-undo ops
    rejected: list[int] = []

    def valid_amount(tok: str) -> bool:
        return tok.isascii() and tok.isdigit()

    def fail(i: int) -> None:
        rejected.append(i)

    for i, op in enumerate(ops):
        tokens = op.split(" ")
        if not tokens or tokens[0] == "":
            fail(i)
            continue
        verb = tokens[0]
        args = tokens[1:]

        if verb == "undo":
            if len(args) != 0 or not history:
                fail(i)
                continue
            record = history.pop()
            kind = record[0]
            if kind == "open":
                _, name = record
                del accounts[name]
            elif kind == "deposit":
                _, name, amt = record
                accounts[name]["balance"] -= amt
            elif kind == "withdraw":
                _, name, amt = record
                accounts[name]["balance"] += amt
            elif kind == "transfer":
                _, src, dst, amt = record
                accounts[dst]["balance"] -= amt
                accounts[src]["balance"] += amt
            elif kind == "freeze":
                _, name = record
                accounts[name]["frozen"] = False
            elif kind == "unfreeze":
                _, name = record
                accounts[name]["frozen"] = True
            continue

        if verb == "open":
            if len(args) != 2 or not valid_amount(args[1]):
                fail(i)
                continue
            name, amt = args[0], int(args[1])
            if name in accounts:
                fail(i)
                continue
            accounts[name] = {"balance": amt, "frozen": False}
            history.append(("open", name))

        elif verb == "deposit":
            if len(args) != 2 or not valid_amount(args[1]):
                fail(i)
                continue
            name, amt = args[0], int(args[1])
            if amt <= 0 or name not in accounts:
                fail(i)
                continue
            accounts[name]["balance"] += amt
            history.append(("deposit", name, amt))

        elif verb == "withdraw":
            if len(args) != 2 or not valid_amount(args[1]):
                fail(i)
                continue
            name, amt = args[0], int(args[1])
            if amt <= 0 or name not in accounts:
                fail(i)
                continue
            acc = accounts[name]
            if acc["frozen"] or acc["balance"] < amt:
                fail(i)
                continue
            acc["balance"] -= amt
            history.append(("withdraw", name, amt))

        elif verb == "transfer":
            if len(args) != 3 or not valid_amount(args[2]):
                fail(i)
                continue
            src, dst, amt = args[0], args[1], int(args[2])
            if amt <= 0 or src == dst or src not in accounts or dst not in accounts:
                fail(i)
                continue
            if accounts[src]["frozen"] or accounts[src]["balance"] < amt:
                fail(i)
                continue
            accounts[src]["balance"] -= amt
            accounts[dst]["balance"] += amt
            history.append(("transfer", src, dst, amt))

        elif verb == "freeze":
            if len(args) != 1 or args[0] not in accounts or accounts[args[0]]["frozen"]:
                fail(i)
                continue
            accounts[args[0]]["frozen"] = True
            history.append(("freeze", args[0]))

        elif verb == "unfreeze":
            if len(args) != 1 or args[0] not in accounts or not accounts[args[0]]["frozen"]:
                fail(i)
                continue
            accounts[args[0]]["frozen"] = False
            history.append(("unfreeze", args[0]))

        else:
            fail(i)

    balances = {name: acc["balance"] for name, acc in accounts.items()}
    return balances, rejected
