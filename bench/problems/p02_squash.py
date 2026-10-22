RUNG = 1
FUNC = "squash"
SIGNATURE = "def squash(s: str) -> str:"
STATEMENT = r"""Compress a string by splitting it into maximal runs of the same character and writing each run as follows:
- A run of length 3 or more of character `c` becomes the decimal run length followed by `esc(c)`.
- A run of length 1 or 2 is written as `esc(c)` once per character.

`esc(c)` is `c` itself, except when `c` is a decimal digit (`0`-`9`) or a backslash (`\`). Those are written as a backslash followed by `c`.

Examples (Python string literals):
- `squash("aaab")` returns `"3ab"`.
- `squash("aabccccccccccc")` returns `"aab11c"`.
- `squash("111")` returns `"3\\1"`, the four characters `3`, `\`, `1`.
- `squash("a1")` returns `"a\\1"`.
- `squash("\\\\")` (two backslashes) returns `"\\\\\\\\"` (four backslashes).
- `squash("")` returns `""`.

Constraints: `0 <= len(s) <= 200000`. `s` contains printable ASCII characters only."""


def _esc(c):
    return "\\" + c if c.isdigit() or c == "\\" else c


def ref(s):
    out = []; i = 0
    while i < len(s):
        j = i
        while j < len(s) and s[j] == s[i]:
            j += 1
        L = j - i
        out.append(f"{L}{_esc(s[i])}" if L >= 3 else _esc(s[i]) * L)
        i = j
    return "".join(out)


def brute(s):
    import itertools
    r = ""
    for c, g in itertools.groupby(s):
        n = len(list(g)); e = ("\\" + c) if c in "0123456789\\" else c
        r += (str(n) + e) if n > 2 else e * n
    return r


def small(rng):
    al = rng.choice(["ab", "a1\\", "ab12\\ ", "xyz9"])
    return ("".join(rng.choice(al) * rng.choice([1, 1, 2, 3, 4, 12]) for _ in range(rng.randint(0, 8))),)


def fixed():
    return [("aaab",), ("aabccccccccccc",), ("111",), ("a1",), ("\\\\",), ("",), ("\\\\\\",), ("1111111111",), ("z",)]


def big(rng):
    return [("".join(rng.choice("ab1\\") * rng.randint(1, 30) for _ in range(12000)),)]


WRONG = {
    "no_backslash_escape": """
def squash(s):
    import itertools
    r = []
    for c, g in itertools.groupby(s):
        n = len(list(g)); e = ("\\\\" + c) if c.isdigit() else c
        r.append(f"{n}{e}" if n >= 3 else e * n)
    return "".join(r)
""",
    "threshold_two": """
def squash(s):
    import itertools
    r = []
    for c, g in itertools.groupby(s):
        n = len(list(g)); e = ("\\\\" + c) if (c.isdigit() or c == "\\\\") else c
        r.append(f"{n}{e}" if n >= 2 else e * n)
    return "".join(r)
""",
}

EXAMPLES = [(("aaab",), "3ab"), (("aabccccccccccc",), "aab11c"), (("111",), "3\\1"), (("a1",), "a\\1"),
            (("\\\\",), "\\\\\\\\"), (("",), "")]
