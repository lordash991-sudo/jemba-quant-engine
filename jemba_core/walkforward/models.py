from dataclasses import dataclass


@dataclass(slots=True)
class WalkForwardWindow:
    train_start: int
    train_end: int
    test_start: int
    test_end: int


@dataclass(slots=True)
class WalkForwardResult:
    train_score: float
    test_score: float
    parameters: dict
