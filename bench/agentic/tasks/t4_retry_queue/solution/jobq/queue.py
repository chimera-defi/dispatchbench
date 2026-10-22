import heapq
import itertools

from .job import Job


class JobQueue:
    """Time-ordered job queue. `clock` is a zero-argument callable returning integer seconds."""

    def __init__(self, clock):
        self.clock = clock
        self._heap: list[Job] = []
        self._seq = itertools.count()

    def submit(self, name: str, fn, delay: int = 0) -> Job:
        job = Job(self.clock() + delay, next(self._seq), name, fn)
        heapq.heappush(self._heap, job)
        return job

    def requeue(self, job: Job, run_at: int) -> None:
        job.run_at = run_at
        heapq.heappush(self._heap, job)

    def pop_due(self) -> Job | None:
        """Remove and return the earliest job whose run_at <= now, or None."""
        if self._heap and self._heap[0].run_at <= self.clock():
            return heapq.heappop(self._heap)
        return None

    def __len__(self) -> int:
        return len(self._heap)
