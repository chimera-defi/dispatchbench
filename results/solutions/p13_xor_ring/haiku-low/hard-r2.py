def evolve(state: str, offsets: list[int], t: int) -> str:
    n = len(state)

    # Reduce offsets mod n and keep only those appearing an odd number of times.
    parity = [0] * n
    for d in offsets:
        parity[d % n] ^= 1
    S = [e for e in range(n) if parity[e]]

    def apply(v, exps):
        # new[i] = XOR of v[(i + e) % n] over e in exps
        new = [0] * n
        for e in exps:
            rot = v[e:] + v[:e]
            new = [a ^ b for a, b in zip(new, rot)]
        return new

    v = [int(c) for c in state]

    # Over GF(2), P(x)^(2^j) = P(x^(2^j)), so the exponent set of P^(2^j)
    # is the set of e * 2^j mod n, with duplicates cancelling.
    # Apply P^(2^j) for each set bit of t; all these operators commute.
    while t:
        if t & 1:
            v = apply(v, S)
        t >>= 1
        if t:
            parity = [0] * n
            for e in S:
                parity[(2 * e) % n] ^= 1
            S = [e for e in range(n) if parity[e]]

    return ''.join(str(b) for b in v)
