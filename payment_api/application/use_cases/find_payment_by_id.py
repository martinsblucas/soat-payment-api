"""Use case for creating a new payment"""

import logging

from payment_api.application.commands import FindPaymentByIdCommand
from payment_api.domain.entities import PaymentOut
from payment_api.domain.ports import PaymentRepository

logger = logging.getLogger(__name__)


class FindPaymentByIdUseCase:
    """Use case to handle the finding of a payment by its ID"""

    def __init__(self, payment_repository: PaymentRepository):
        self.payment_repository = payment_repository

    async def execute(self, command: FindPaymentByIdCommand) -> PaymentOut:
        """Execute the use case to find a payment by its ID

        :param command: command containing payment ID
        :type command: FindPaymentByIdCommand
        :return: Payment entity corresponding to the given ID
        :rtype: PaymentOut
        :raises NotFound: if payment is not found
        :raises PersistenceError: if there is an error during data retrieval from
            the repository
        """

        logger.info(
            "Called the use case to find payment with ID %s", command.payment_id
        )

        return await self.payment_repository.find_by_id(payment_id=command.payment_id)
