class ConfigError(ValueError):
    """Raised for malformed config text. `line` is the 1-based line number, or None."""

    def __init__(self, message: str, line: int | None = None):
        super().__init__(f"line {line}: {message}" if line else message)
        self.line = line
