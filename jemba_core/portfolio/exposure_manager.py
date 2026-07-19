from dataclasses import dataclass


@dataclass(slots=True)
class ExposureResult:
    allowed: bool
    exposure: float


class ExposureManager:

    def __init__(self, max_exposure: float = 0.60):
        self.max_exposure = max_exposure

    def check(self, current_exposure: float, new_position: float) -> ExposureResult:

        if current_exposure < 0:
            raise ValueError("INVALID_CURRENT_EXPOSURE")

        if new_position < 0:
            raise ValueError("INVALID_POSITION")

        total = current_exposure + new_position

        return ExposureResult(
            allowed=total <= self.max_exposure,
            exposure=total,
        )
