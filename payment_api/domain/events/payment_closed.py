"""Payment closed event module"""

from pydantic import Field

from .domain_event import DomainEvent


class PaymentClosedEvent(DomainEvent):
    """Event representing the closure of a payment process"""

    payment_id: str = Field(description="Unique identifier for the closed payment")
