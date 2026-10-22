def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:
    balances: dict[str, int] = {}
    frozen: set[str] = set()
    history: list[tuple] = []
    rejected: list[int] = []

    def parse_amount(s: str):
        if not s or any(ch < "0" or ch > "9" for ch in s):
            return None
        value = 0
        for ch in s:
            value = value * 10 + ord(ch) - ord("0")
        return value

    for i, op in enumerate(ops):
        tokens = op.split(" ")
        verb = tokens[0]
        success = False

        if verb == "undo" and len(tokens) == 1:
            if history:
                action = history.pop()
                kind = action[0]

                if kind == "open":
                    del balances[action[1]]
                    frozen.discard(action[1])
                elif kind == "delta":
                    balances[action[1]] += action[2]
                elif kind == "transfer":
                    a, b, amount = action[1:]
                    balances[a] += amount
                    balances[b] -= amount
                elif kind == "frozen":
                    account, was_frozen = action[1:]
                    if was_frozen:
                        frozen.add(account)
                    else:
                        frozen.discard(account)
                success = True

        elif verb == "open" and len(tokens) == 3:
            account = tokens[1]
            amount = parse_amount(tokens[2])
            if amount is not None and account not in balances:
                balances[account] = amount
                history.append(("open", account))
                success = True

        elif verb == "deposit" and len(tokens) == 3:
            account = tokens[1]
            amount = parse_amount(tokens[2])
            if amount is not None and amount > 0 and account in balances:
                balances[account] += amount
                history.append(("delta", account, -amount))
                success = True

        elif verb == "withdraw" and len(tokens) == 3:
            account = tokens[1]
            amount = parse_amount(tokens[2])
            if (amount is not None and amount > 0 and account in balances
                    and account not in frozen and balances[account] >= amount):
                balances[account] -= amount
                history.append(("delta", account, amount))
                success = True

        elif verb == "transfer" and len(tokens) == 4:
            a, b = tokens[1], tokens[2]
            amount = parse_amount(tokens[3])
            if (amount is not None and amount > 0 and a != b
                    and a in balances and b in balances and a not in frozen
                    and balances[a] >= amount):
                balances[a] -= amount
                balances[b] += amount
                history.append(("transfer", a, b, amount))
                success = True

        elif verb in ("freeze", "unfreeze") and len(tokens) == 2:
            account = tokens[1]
            should_be_frozen = verb == "freeze"
            if (account in balances
                    and ((should_be_frozen and account not in frozen)
                         or (not should_be_frozen and account in frozen))):
                was_frozen = account in frozen
                if should_be_frozen:
                    frozen.add(account)
                else:
                    frozen.remove(account)
                history.append(("frozen", account, was_frozen))
                success = True

        if not success:
            rejected.append(i)

    return balances, rejected
