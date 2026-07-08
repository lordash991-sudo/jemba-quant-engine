from jemba_core.engine.scheduler import Scheduler


def test_scheduler_run_once():
    scheduler = Scheduler(interval_seconds=1)
    calls = []

    def task():
        calls.append("ok")
        return "done"

    result = scheduler.run_once(task)

    assert result == "done"
    assert calls == ["ok"]
    assert scheduler.cycles_executed == 1
    assert scheduler.last_run_at is not None


def test_scheduler_run_forever_with_max_cycles():
    scheduler = Scheduler(interval_seconds=0, max_cycles=3)
    calls = []

    def task():
        calls.append("ok")

    scheduler.run_forever(task)

    assert len(calls) == 3
    assert scheduler.cycles_executed == 3
    assert scheduler.running is False
