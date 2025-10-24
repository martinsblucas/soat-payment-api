"""Domain events module"""

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class DomainEvent(BaseModel):
    """Abstract base class for domain events"""

    id: UUID = Field(
        description="Unique identifier for the event", default_factory=uuid4
    )

    occurred_at: datetime = Field(
        description="Timestamp when the event occurred", default_factory=datetime.now
    )

    version: int = Field(description="Version of the event", default=1)

    # Make the model immutable as events should be immutable
    model_config = ConfigDict(frozen=True)

    def get_name(self) -> str:
        """Get the name of the domain event

        :rtype: str
        :return: The name of the domain event
        """
        return self.__class__.__name__
