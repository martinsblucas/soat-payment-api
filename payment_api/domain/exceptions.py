"""The domain exeptions"""


class DomainException(Exception):
    """The domain base exception"""

    def __init__(self, message="An error occurred"):
        super().__init__(message)


class NotFound(DomainException):
    """The not found exception."""

    def __init__(self, message="Not found"):
        super().__init__(message)


class PersistenceError(DomainException):
    """If an error occurs trying to persist or retrieve data"""

    def __init__(
        self, message="An error occurred while trying to persist or retrieve data"
    ):
        super().__init__(message)


class PaymentCreationError(DomainException):
    """An error to be raised by the payment gateway implementations when an error occurs
    trying to create a payment. Also to be used by the create payment use case when an
    error occurs during the creation process."""

    def __init__(self, message="An error occurred while trying to create a payment"):
        super().__init__(message)


class EventPublishingError(DomainException):
    """An error to be raised by the event publisher implementations when an error occurs
    trying to publish an event."""

    def __init__(self, message="An error occurred while trying to publish an event"):
        super().__init__(message)
