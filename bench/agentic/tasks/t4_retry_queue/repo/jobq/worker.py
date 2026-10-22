from .queue import JobQueue


class Worker:
    def __init__(self, queue: JobQueue):
        self.queue = queue
        self.done: list[str] = []     # names of jobs that succeeded, in completion order

    def run_due(self) -> int:
        """Run every job that is due now, earliest first. Returns how many jobs ran."""
        ran = 0
        while (job := self.queue.pop_due()) is not None:
            job.fn()
            self.done.append(job.name)
            ran += 1
        return ran
