Add value references to the `cfg` package in this repository. Work in the current directory.

After parsing, `load()` must resolve references inside values:

- `${key}` is replaced by the resolved value of `key` in the same section.
- `${section.key}` is replaced by the resolved value of `key` in `section`. The part before the last dot is the section name, so `${a.b.c}` means key `c` of section `a.b`. `${.key}` means key `key` of the unnamed section `""` that holds entries before the first `[section]`.
- `$$` is a literal `$`. A `$` that starts neither `${` nor `$$` is an error.
- References can be nested through other values (`a = ${b}`, `b = ${c}`) and a value can contain several references and plain text.
- A reference to a missing section or key raises `ConfigError` whose message contains the missing name exactly as written in the reference, for example `unknown reference: db.hostt`.
- A reference cycle raises `ConfigError` whose message is exactly `reference cycle: ` followed by the chain of fully qualified names joined with ` -> `, starting and ending with the first key that repeats, for example `reference cycle: a.x -> a.y -> a.x`. Fully qualified means `section.key`, and `.key` for the unnamed section. Keys are resolved in file order, and references within a value from left to right, so the reported cycle is the first one reached that way.
- An unterminated `${` is a `ConfigError` too.
- For errors that come from resolving a value, set `ConfigError.line` to the line number where the key being resolved first (the outermost one) was defined.

Keep the existing parser behaviour. Add tests in `tests/test_refs.py`. Run `python3 -m pytest -q`; all tests must pass.
