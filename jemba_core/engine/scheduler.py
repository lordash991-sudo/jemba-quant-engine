import time
from datetime import datetime, UTC


class Scheduler:

    def __init__(
        self,
        interval_seconds: int = 60,
        max_cycles: int | None = None,
    ):
        self.interval_seconds = int(interval_seconds)
        self.max_cycles = max_cycles
        self.running = False
        self.cycles_executed = 0
        self.last_run_at = None

    def run_once(self, task, *args, **kwargs):
        self.last_run_at = datetime.now(UTC)
        self.cycles_executed += 1

        return task(*args, **kwargs)

    def run_forever(self, task, *args, **kwargs):
        self.running = True

        while self.running:
            self.run_once(task, *args, **kwargs)

            if (
                self.max_cycles is not None
                and self.cycles_executed >= self.max_cycles
            ):
                self.stop()
                break

            time.sleep(self.interval_seconds)

    def stop(self):
        self.running = False

    def summary(self):
        return {
            "running": self.running,
            "cycles_executed": self.cycles_executed,
            "interval_seconds": self.interval_seconds,
            "last_run_at": self.last_run_at,
        }
