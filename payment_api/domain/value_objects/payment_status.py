"""Payment status value object module"""

from enum import Enum, unique


@unique
class PaymentStatus(str, Enum):
    """Enumeration of possible payment statuses."""

    OPENED = "OPENED"
    CLOSED = "CLOSED"
    EXPIRED = "EXPIRED"
