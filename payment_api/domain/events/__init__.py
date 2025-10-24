"""Events module package"""

from .domain_event import DomainEvent
from .payment_closed import PaymentClosedEvent

__all__ = ["DomainEvent", "PaymentClosedEvent"]
