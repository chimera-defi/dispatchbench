def evolve(state: str, offsets: list[int], t: int) -> str:
    n = len(state)

    # Offsets are taken mod n; a repeated offset cancels, so keep parities only.
    c = [0] * n
    for d in offsets:
        c[d % n] ^= 1

    # new[i] = XOR_k c[k] * old[(i + k) mod n] is a cyclic convolution with
    # r[j] = c[-j mod n], i.e. new[i] = XOR_j r[j] * old[(i - j) mod n].
    r = [0] * n
    for k in range(n):
        r[(-k) % n] = c[k]

    def mul(a: list[int], b: list[int]) -> list[int]:
        # Carry-less cyclic product over GF(2), done with big-integer multiplication.
        # Each coefficient sits in its own 16-bit digit, so sums up to n never overflow.
        A = int.from_bytes(bytes(v for bit in a for v in (bit, 0)), "little")
        B = int.from_bytes(bytes(v for bit in b for v in (bit, 0)), "little")
        bs = (A * B).to_bytes(4 * n + 4, "little")
        out = [0] * n
        for j in range(2 * n):
            if bs[2 * j] & 1:
                out[j % n] ^= 1
        return out

    # Compute r^t in the ring GF(2)[x] / (x^n - 1) by binary exponentiation.
    result = [0] * n
    result[0] = 1  # identity element x^0
    base = r
    while t:
        if t & 1:
            result = mul(result, base)
        t >>= 1
        if t:
            base = mul(base, base)

    # Apply the resulting operator to the state.
    old = [1 if ch == "1" else 0 for ch in state]
    new = mul(result, old)
    return "".join("1" if bit else "0" for bit in new)
