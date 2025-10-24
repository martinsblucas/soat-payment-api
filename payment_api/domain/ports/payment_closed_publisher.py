"""Payment closed publisher port"""

from abc import ABC, abstractmethod

from payment_api.domain.events import PaymentClosedEvent


class PaymentClosedPublisher(ABC):
    """Port for publishing payment closed events"""

    @abstractmethod
    async def publish(self, event: PaymentClosedEvent) -> None:
        """Publish a payment closed event

        :param event: The payment closed event to publish
        :return: None
        :raises EventPublishingError: If an error occurs while publishing the event
        """
