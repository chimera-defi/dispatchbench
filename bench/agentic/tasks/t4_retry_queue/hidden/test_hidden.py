import pytest
from jobq.queue import JobQueue
from jobq.worker import Worker


class Clock:
    def __init__(self): self.t = 0
    def __call__(self): return self.t


def flaky(n_failures, log, name):
    state = {"n": 0}
    def fn():
        state["n"] += 1; log.append((name, state["n"]))
        if state["n"] <= n_failures: raise RuntimeError(f"{name} boom {state['n']}")
    return fn


def run_until(clk, w, end):
    while clk.t <= end:
        w.run_due(); clk.t += 1


def test_backoff_schedule_and_cap():
    clk = Clock(); q = JobQueue(clk); w = Worker(q, max_attempts=6, base_delay=3, max_delay=10); log = []; times = []
    def fn():
        times.append(clk.t); raise ValueError("x")
    q.submit("j", fn)
    run_until(clk, w, 100)
    assert times == [0, 3, 9, 19, 29, 39]            # delays 3, 6, 10 (capped from 12), 10, 10
    assert w.dead == [("j", 6, "ValueError('x')")]
    assert w.stats() == {"succeeded": 0, "failed_attempts": 6, "dead": 1}


def test_recovers_before_limit():
    clk = Clock(); q = JobQueue(clk); w = Worker(q); log = []
    q.submit("a", flaky(2, log, "a"))
    run_until(clk, w, 20)
    assert w.done == ["a"] and w.dead == [] and log == [("a", 1), ("a", 2), ("a", 3)]
    assert w.stats() == {"succeeded": 1, "failed_attempts": 2, "dead": 0}


def test_requeued_job_not_rerun_in_same_call():
    clk = Clock(); q = JobQueue(clk); w = Worker(q, max_attempts=5, base_delay=1); log = []
    q.submit("a", flaky(10, log, "a"))
    assert w.run_due() == 1 and len(log) == 1
    assert w.run_due() == 0
    clk.t = 1; assert w.run_due() == 1


def test_delay_counts_from_attempt_time_not_run_at():
    clk = Clock(); q = JobQueue(clk); w = Worker(q, base_delay=4); times = []
    def fn():
        times.append(clk.t); raise RuntimeError
    q.submit("late", fn)
    clk.t = 7; w.run_due()           # first attempt happens at 7, although run_at was 0
    run_until(clk, w, 40)
    assert times == [7, 11, 19]


def test_seq_preserved_for_ties():
    clk = Clock(); q = JobQueue(clk); w = Worker(q, base_delay=2); log = []
    q.submit("first", flaky(1, log, "first"))
    w.run_due()                      # first fails at 0, due again at 2
    q.submit("second", lambda: log.append(("second", 1)), delay=2)
    clk.t = 2; assert w.run_due() == 2
    assert log[-2:] == [("first", 2), ("second", 1)]


def test_base_exception_propagates_without_requeue():
    clk = Clock(); q = JobQueue(clk); w = Worker(q)
    def stop(): raise KeyboardInterrupt
    q.submit("k", stop)
    with pytest.raises(KeyboardInterrupt): w.run_due()
    clk.t = 100; assert w.run_due() == 0 and w.dead == []


@pytest.mark.parametrize("kw", [dict(max_attempts=0), dict(base_delay=0), dict(base_delay=5, max_delay=4)])
def test_bad_settings(kw):
    with pytest.raises(ValueError): Worker(JobQueue(Clock()), **kw)


def test_attempts_counted():
    clk = Clock(); q = JobQueue(clk); w = Worker(q, max_attempts=2); log = []
    j = q.submit("a", flaky(1, log, "a")); run_until(clk, w, 10)
    assert j.attempts == 2 and w.done == ["a"]
    assert Worker(q).stats() == {"succeeded": 0, "failed_attempts": 0, "dead": 0}
