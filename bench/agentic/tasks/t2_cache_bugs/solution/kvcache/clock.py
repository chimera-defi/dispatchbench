class FakeClock:
    """Manually advanced clock for tests. Time is in whole seconds."""

    def __init__(self, now: int = 0):
        self.now = now

    def __call__(self) -> int:
        return self.now

    def advance(self, seconds: int) -> None:
        self.now += seconds
