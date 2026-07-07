from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4


@dataclass(slots=True)
class BaseEvent:
    event_type: str
    source: str

    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    version: str = "1.0"
    metadata: dict = field(default_factory=dict)
