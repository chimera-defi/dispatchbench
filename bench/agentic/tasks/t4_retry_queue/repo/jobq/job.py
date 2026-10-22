from dataclasses import dataclass, field


@dataclass(order=True)
class Job:
    run_at: int                     # earliest time the job may run
    seq: int                        # insertion order, breaks ties between equal run_at
    name: str = field(compare=False)
    fn: object = field(compare=False, repr=False)  # zero-argument callable
    attempts: int = field(default=0, compare=False)
