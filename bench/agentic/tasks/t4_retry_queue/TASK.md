Add retries to the `jobq` package in this repository. Work in the current directory.

1. `Worker(queue, max_attempts=3, base_delay=2, max_delay=60)`. Existing calls `Worker(queue)` must keep working. Reject `max_attempts < 1`, `base_delay < 1` or `max_delay < base_delay` with `ValueError`.
2. When a job's `fn` raises an `Exception`, the attempt counts as failed. If the job has now failed `max_attempts` times in total, it is moved to `worker.dead`, a list of `(name, attempts, repr_of_last_exception)` tuples in the order jobs died. Otherwise it is put back on the queue to run again after a delay of `min(max_delay, base_delay * 2 ** (failures - 1))` seconds, counted from the time of the failed attempt (the clock value when the attempt ran), where `failures` is how many times that job has failed so far. `job.attempts` counts attempts made (successful or not).
3. Exceptions that are not `Exception` subclasses (for example `KeyboardInterrupt`) must propagate unchanged and the job must not be requeued.
4. A retried job keeps its original `seq`, so among jobs due at the same time it keeps its place relative to jobs submitted after it.
5. `run_due()` runs only jobs that were due when it started looking at the queue: a job requeued during this call is not run again in the same call, even if its delay rounds to "now". It returns the number of attempts made (successful or failed).
6. `Worker.stats()` returns `{"succeeded": int, "failed_attempts": int, "dead": int}`.

Add tests in `tests/test_retry.py`. Run `python3 -m pytest -q`; all tests must pass.
