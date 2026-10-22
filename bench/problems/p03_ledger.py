RUNG = 2
FUNC = "ledger"
SIGNATURE = "def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:"
STATEMENT = """\
Process a list of bank operations, in order. Each operation is a string of tokens separated by single spaces. An account name is any token. An amount `N` is valid only if it consists entirely of the decimal digits 0-9, with no sign; leading zeros are allowed (`"007"` is 7).

Operations:
- `open A N`: create account `A` with balance `N`, where `N >= 0`. Fails if `A` already exists.
- `deposit A N`: add `N` to `A`. Requires `N > 0` and that `A` exists. Deposits are allowed while `A` is frozen.
- `withdraw A N`: subtract `N` from `A`. Requires `N > 0`, that `A` exists and is not frozen, and that its balance is at least `N`.
- `transfer A B N`: move `N` from `A` to `B`. Requires `N > 0`, `A != B`, both accounts exist, `A` is not frozen, and the balance of `A` is at least `N`. `B` may be frozen.
- `freeze A`: requires that `A` exists and is not frozen.
- `unfreeze A`: requires that `A` exists and is frozen.
- `undo`: reverts the most recent successful operation that has not already been reverted, ignoring `undo` operations themselves. Reverting `open` removes the account. Reverting `freeze` or `unfreeze` restores the previous frozen state. An `undo` with nothing left to revert fails. An `undo` can never itself be reverted.

Any operation that breaks a rule, has an unknown verb, has the wrong number of tokens, or has an invalid amount fails. A failed operation changes nothing.

Return a pair `(balances, rejected)`:
- `balances` maps every account that exists at the end to its balance.
- `rejected` is the ascending list of 0-based indices of the operations that failed.

Example: `ledger(["open a 10", "open b 0", "transfer a b 4", "freeze a", "deposit a 5", "withdraw a 1", "undo", "undo", "withdraw a 1", "undo", "undo", "undo", "undo", "undo"])` returns `({}, [5, 13])`. Index 5 fails because `a` is frozen. The undos at 6 and 7 revert the deposit and the freeze. Index 8 withdraws 1, and index 9 reverts it. Indices 10, 11 and 12 revert the transfer, `open b` and `open a`. Index 13 has nothing left to revert.

Constraints: `0 <= len(ops) <= 20000`."""


def _amt(tok):
    return int(tok) if tok.isascii() and tok.isdigit() else None


def ref(ops):
    bal = {}; frozen = set(); stack = []; rej = []
    for i, op in enumerate(ops):
        t = op.split(" "); v = t[0]; ok = False
        if v == "open" and len(t) == 3:
            n = _amt(t[2])
            if n is not None and t[1] not in bal:
                bal[t[1]] = n; stack.append(("open", t[1])); ok = True
        elif v == "deposit" and len(t) == 3:
            n = _amt(t[2])
            if n and t[1] in bal:
                bal[t[1]] += n; stack.append(("dep", t[1], n)); ok = True
        elif v == "withdraw" and len(t) == 3:
            n = _amt(t[2]); a = t[1]
            if n and a in bal and a not in frozen and bal[a] >= n:
                bal[a] -= n; stack.append(("dep", a, -n)); ok = True
        elif v == "transfer" and len(t) == 4:
            n = _amt(t[3]); a, b = t[1], t[2]
            if n and a != b and a in bal and b in bal and a not in frozen and bal[a] >= n:
                bal[a] -= n; bal[b] += n; stack.append(("xfer", a, b, n)); ok = True
        elif v == "freeze" and len(t) == 2:
            if t[1] in bal and t[1] not in frozen:
                frozen.add(t[1]); stack.append(("frz", t[1], True)); ok = True
        elif v == "unfreeze" and len(t) == 2:
            if t[1] in bal and t[1] in frozen:
                frozen.discard(t[1]); stack.append(("frz", t[1], False)); ok = True
        elif v == "undo" and len(t) == 1 and stack:
            u = stack.pop(); ok = True
            if u[0] == "open":
                del bal[u[1]]; frozen.discard(u[1])
            elif u[0] == "dep":
                bal[u[1]] -= u[2]
            elif u[0] == "xfer":
                bal[u[1]] += u[3]; bal[u[2]] -= u[3]
            else:
                (frozen.discard if u[2] else frozen.add)(u[1])
        if not ok:
            rej.append(i)
    return (bal, rej)


def brute(ops):
    # Independent: keep the list of live successful ops and rebuild state by replaying it.
    def replay(live):
        b, fz = {}, set()
        for t in live:
            if t[0] == "open": b[t[1]] = int(t[2])
            elif t[0] == "deposit": b[t[1]] += int(t[2])
            elif t[0] == "withdraw": b[t[1]] -= int(t[2])
            elif t[0] == "transfer": b[t[1]] -= int(t[3]); b[t[2]] += int(t[3])
            elif t[0] == "freeze": fz.add(t[1])
            else: fz.discard(t[1])
        return b, fz
    live = []; rej = []
    for i, op in enumerate(ops):
        t = op.split(" ")
        b, fz = replay(live)
        valid_amt = lambda s: all(ch in "0123456789" for ch in s) and len(s) > 0
        good = False
        if t == ["undo"]:
            good = bool(live)
            if good: live.pop()
        else:
            shape = {"open": 3, "deposit": 3, "withdraw": 3, "transfer": 4, "freeze": 2, "unfreeze": 2}
            if shape.get(t[0]) == len(t):
                if t[0] == "open": good = valid_amt(t[2]) and t[1] not in b
                elif t[0] == "deposit": good = valid_amt(t[2]) and int(t[2]) > 0 and t[1] in b
                elif t[0] == "withdraw": good = valid_amt(t[2]) and int(t[2]) > 0 and t[1] in b and t[1] not in fz and b[t[1]] >= int(t[2])
                elif t[0] == "transfer": good = valid_amt(t[3]) and int(t[3]) > 0 and t[1] != t[2] and t[1] in b and t[2] in b and t[1] not in fz and b[t[1]] >= int(t[3])
                elif t[0] == "freeze": good = t[1] in b and t[1] not in fz
                else: good = t[1] in b and t[1] in fz
            if good: live.append(t)
        if not good: rej.append(i)
    return (replay(live)[0], rej)


def _gen(rng, n, accts):
    ops = []
    for _ in range(n):
        a, b = rng.choice(accts), rng.choice(accts)
        amt = rng.choice([str(rng.randint(0, 20)), str(rng.randint(1, 9)), "0", "007", "-3", "x", "1.5", ""])
        v = rng.choice(["open", "open", "deposit", "withdraw", "transfer", "transfer", "freeze", "unfreeze", "undo", "undo", "undo", "bogus"])
        if v in ("open", "deposit", "withdraw"): op = f"{v} {a} {amt}"
        elif v == "transfer": op = f"{v} {a} {b} {amt}"
        elif v in ("freeze", "unfreeze"): op = f"{v} {a}"
        elif v == "undo": op = rng.choice(["undo", "undo", "undo", "undo x"])
        else: op = f"close {a}"
        ops.append(op)
    return ops


def small(rng):
    return (_gen(rng, rng.randint(0, 14), ["a", "b", "c"][:rng.randint(1, 3)]),)


def fixed():
    ex = ["open a 10", "open b 0", "transfer a b 4", "freeze a", "deposit a 5", "withdraw a 1", "undo", "undo",
          "withdraw a 1", "undo", "undo", "undo", "undo", "undo"]
    return [(ex,), ([],), (["undo"],), (["open a 5", "open a 6", "undo", "open a 6"],),
            (["open a 1", "freeze a", "freeze a", "unfreeze a", "undo", "withdraw a 1", "undo", "undo", "withdraw a 1"],),
            (["open a 3", "open b 1", "freeze b", "transfer a b 3", "transfer b a 1", "transfer a a 0", "deposit a 0", "open c 007"],)]


def big(rng):
    return [(_gen(rng, 20000, [f"u{i}" for i in range(40)]),)]


WRONG = {
    "frozen_blocks_deposit": """
def ledger(ops):
    bal = {}; fz = set(); st = []; rej = []
    amt = lambda s: int(s) if s.isdigit() else None
    for i, op in enumerate(ops):
        t = op.split(" "); ok = False
        if t[0] == "open" and len(t) == 3 and amt(t[2]) is not None and t[1] not in bal:
            bal[t[1]] = amt(t[2]); st.append(("o", t[1])); ok = True
        elif t[0] == "deposit" and len(t) == 3 and amt(t[2]) and t[1] in bal and t[1] not in fz:
            bal[t[1]] += amt(t[2]); st.append(("d", t[1], amt(t[2]))); ok = True
        elif t[0] == "withdraw" and len(t) == 3 and amt(t[2]) and t[1] in bal and t[1] not in fz and bal[t[1]] >= amt(t[2]):
            bal[t[1]] -= amt(t[2]); st.append(("d", t[1], -amt(t[2]))); ok = True
        elif t[0] == "transfer" and len(t) == 4 and amt(t[3]) and t[1] != t[2] and t[1] in bal and t[2] in bal and t[1] not in fz and bal[t[1]] >= amt(t[3]):
            n = amt(t[3]); bal[t[1]] -= n; bal[t[2]] += n; st.append(("x", t[1], t[2], n)); ok = True
        elif t[0] == "freeze" and len(t) == 2 and t[1] in bal and t[1] not in fz:
            fz.add(t[1]); st.append(("f", t[1], True)); ok = True
        elif t[0] == "unfreeze" and len(t) == 2 and t[1] in fz:
            fz.discard(t[1]); st.append(("f", t[1], False)); ok = True
        elif t == ["undo"] and st:
            u = st.pop(); ok = True
            if u[0] == "o": del bal[u[1]]; fz.discard(u[1])
            elif u[0] == "d": bal[u[1]] -= u[2]
            elif u[0] == "x": bal[u[1]] += u[3]; bal[u[2]] -= u[3]
            else: (fz.discard if u[2] else fz.add)(u[1])
        if not ok: rej.append(i)
    return bal, rej
""",
    "undo_only_balances": """
def ledger(ops):
    bal = {}; fz = set(); st = []; rej = []
    amt = lambda s: int(s) if s.isdigit() else None
    for i, op in enumerate(ops):
        t = op.split(" "); ok = False
        if t[0] == "open" and len(t) == 3 and amt(t[2]) is not None and t[1] not in bal:
            bal[t[1]] = amt(t[2]); st.append(("o", t[1])); ok = True
        elif t[0] == "deposit" and len(t) == 3 and amt(t[2]) and t[1] in bal:
            bal[t[1]] += amt(t[2]); st.append(("d", t[1], amt(t[2]))); ok = True
        elif t[0] == "withdraw" and len(t) == 3 and amt(t[2]) and t[1] in bal and t[1] not in fz and bal[t[1]] >= amt(t[2]):
            bal[t[1]] -= amt(t[2]); st.append(("d", t[1], -amt(t[2]))); ok = True
        elif t[0] == "transfer" and len(t) == 4 and amt(t[3]) and t[1] != t[2] and t[1] in bal and t[2] in bal and t[1] not in fz and bal[t[1]] >= amt(t[3]):
            n = amt(t[3]); bal[t[1]] -= n; bal[t[2]] += n; st.append(("x", t[1], t[2], n)); ok = True
        elif t[0] == "freeze" and len(t) == 2 and t[1] in bal and t[1] not in fz:
            fz.add(t[1]); ok = True
        elif t[0] == "unfreeze" and len(t) == 2 and t[1] in fz:
            fz.discard(t[1]); ok = True
        elif t == ["undo"] and st:
            u = st.pop(); ok = True
            if u[0] == "o": del bal[u[1]]; fz.discard(u[1])
            elif u[0] == "d": bal[u[1]] -= u[2]
            else: bal[u[1]] += u[3]; bal[u[2]] -= u[3]
        if not ok: rej.append(i)
    return bal, rej
""",
}

EXAMPLES = [((fixed()[0][0],), ({}, [5, 13]))]
