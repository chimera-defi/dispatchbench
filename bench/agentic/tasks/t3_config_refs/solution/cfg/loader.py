from .errors import ConfigError
from .parser import parse


def _q(section, key):
    return f"{section}.{key}"


def load(text: str) -> dict[str, dict[str, str]]:
    """Parse config text and return the resolved values."""
    lines: dict = {}
    raw = parse(text, lines)
    done: dict = {}

    def resolve(section, key, stack):
        if (section, key) in done:
            return done[(section, key)]
        if (section, key) in stack:
            i = stack.index((section, key))
            chain = stack[i:] + [(section, key)]
            raise ConfigError("reference cycle: " + " -> ".join(_q(*p) for p in chain))
        stack = stack + [(section, key)]
        v = raw[section][key]; out = []; i = 0
        while i < len(v):
            if v[i] != "$":
                out.append(v[i]); i += 1; continue
            if v[i:i + 2] == "$$":
                out.append("$"); i += 2; continue
            if v[i:i + 2] != "${":
                raise ConfigError(f"stray $ in {_q(section, key)}")
            j = v.find("}", i)
            if j < 0:
                raise ConfigError(f"unterminated ${{ in {_q(section, key)}")
            name = v[i + 2:j]
            if "." in name:
                s, _, k = name.rpartition(".")
            else:
                s, k = section, name
            if s not in raw or k not in raw[s]:
                raise ConfigError(f"unknown reference: {name}")
            out.append(resolve(s, k, stack)); i = j + 1
        done[(section, key)] = "".join(out)
        return done[(section, key)]

    result = {}
    for section, kv in raw.items():
        result[section] = {}
        for key in kv:
            try:
                result[section][key] = resolve(section, key, [])
            except ConfigError as e:
                if e.line is None:
                    raise ConfigError(str(e), lines[(section, key)]) from None
                raise
    return result


def get(config: dict[str, dict[str, str]], dotted: str) -> str:
    """get(cfg, "db.port") reads key "port" of section "db"; a name without a dot reads section ""."""
    section, _, key = dotted.rpartition(".")
    return config[section][key]
