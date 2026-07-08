from dataclasses import dataclass


@dataclass(slots=True)
class TrainingResult:
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1: float
