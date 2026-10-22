from .queue import JobQueue


class Worker:
    def __init__(self, queue: JobQueue, max_attempts: int = 3, base_delay: int = 2, max_delay: int = 60):
        if max_attempts < 1 or base_delay < 1 or max_delay < base_delay:
            raise ValueError("bad retry settings")
        self.queue, self.max_attempts, self.base_delay, self.max_delay = queue, max_attempts, base_delay, max_delay
        self.done: list[str] = []
        self.dead: list[tuple] = []
        self._failed = 0

    def run_due(self) -> int:
        """Run every job that is due now, earliest first. Returns how many attempts ran."""
        batch = []
        while (job := self.queue.pop_due()) is not None:
            batch.append(job)
        for job in batch:
            job.attempts += 1
            now = self.queue.clock()
            try:
                job.fn()
            except Exception as e:
                self._failed += 1
                if job.attempts >= self.max_attempts:
                    self.dead.append((job.name, job.attempts, repr(e)))
                else:
                    delay = min(self.max_delay, self.base_delay * 2 ** (job.attempts - 1))
                    self.queue.requeue(job, now + delay)
                continue
            self.done.append(job.name)
        return len(batch)

    def stats(self) -> dict:
        return {"succeeded": len(self.done), "failed_attempts": self._failed, "dead": len(self.dead)}
