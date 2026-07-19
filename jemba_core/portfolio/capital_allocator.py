from dataclasses import dataclass

@dataclass(slots=True)
class CapitalAllocation:

    risk_percent: float
    leverage: float
    position_fraction: float


class CapitalAllocator:

    def allocate(self, confidence: float) -> CapitalAllocation:

        if not 0 <= confidence <= 1:
            raise ValueError("INVALID_CONFIDENCE")

        if confidence < 0.60:
            return CapitalAllocation(0.00, 0, 0.00)

        if confidence < 0.70:
            return CapitalAllocation(0.50, 5, 0.05)

        if confidence < 0.80:
            return CapitalAllocation(1.00, 10, 0.10)

        if confidence < 0.90:
            return CapitalAllocation(1.50, 20, 0.15)

        if confidence < 0.95:
            return CapitalAllocation(2.00, 30, 0.20)

        return CapitalAllocation(3.00, 50, 0.30)
