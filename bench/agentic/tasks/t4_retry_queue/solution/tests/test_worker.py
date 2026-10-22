from jobq.queue import JobQueue
from jobq.worker import Worker


class Clock:
    def __init__(self): self.t = 0
    def __call__(self): return self.t


def test_runs_in_time_order():
    clk = Clock(); q = JobQueue(clk); w = Worker(q); log = []
    q.submit("b", lambda: log.append("b"), delay=5); q.submit("a", lambda: log.append("a"))
    assert w.run_due() == 1 and log == ["a"]
    clk.t = 5; assert w.run_due() == 1 and w.done == ["a", "b"]
