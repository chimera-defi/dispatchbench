from .parser import parse


def load(text: str) -> dict[str, dict[str, str]]:
    """Parse config text and return the resolved values."""
    return parse(text)


def get(config: dict[str, dict[str, str]], dotted: str) -> str:
    """get(cfg, "db.port") reads key "port" of section "db"; a name without a dot reads section ""."""
    section, _, key = dotted.rpartition(".")
    return config[section][key]
