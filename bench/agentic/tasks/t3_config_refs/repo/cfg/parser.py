from .errors import ConfigError


def parse(text: str) -> dict[str, dict[str, str]]:
    """Parse INI-style text into {section: {key: raw_value}}.

    Sections are `[name]`. Entries are `key = value`; whitespace around key and value is stripped.
    Blank lines and lines starting with `#` are ignored. Entries before the first section go into "".
    A repeated key in the same section is an error.
    """
    out: dict[str, dict[str, str]] = {"": {}}
    section = ""
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip()
            if not section:
                raise ConfigError("empty section name", n)
            out.setdefault(section, {})
            continue
        if "=" not in line:
            raise ConfigError(f"expected key = value, got {line!r}", n)
        key, value = (p.strip() for p in line.split("=", 1))
        if not key:
            raise ConfigError("empty key", n)
        if key in out[section]:
            raise ConfigError(f"duplicate key {key!r}", n)
        out[section][key] = value
    return out
