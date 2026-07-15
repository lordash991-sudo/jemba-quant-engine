from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WalkForwardWindow:
    train_start: int
    train_end: int
    test_start: int
    test_end: int


def generate_walk_forward_windows(
    length: int,
    train_size: int,
    test_size: int,
    *,
    step_size: int | None = None,
) -> list[WalkForwardWindow]:
    if length <= 0:
        raise ValueError("LENGTH_MUST_BE_POSITIVE")

    if train_size <= 0:
        raise ValueError("TRAIN_SIZE_MUST_BE_POSITIVE")

    if test_size <= 0:
        raise ValueError("TEST_SIZE_MUST_BE_POSITIVE")

    step = test_size if step_size is None else step_size

    if step <= 0:
        raise ValueError("STEP_SIZE_MUST_BE_POSITIVE")

    if train_size + test_size > length:
        return []

    windows: list[WalkForwardWindow] = []
    start = 0

    while start + train_size + test_size <= length:
        train_end = start + train_size
        test_end = train_end + test_size

        windows.append(
            WalkForwardWindow(
                train_start=start,
                train_end=train_end,
                test_start=train_end,
                test_end=test_end,
            )
        )

        start += step

    return windows
