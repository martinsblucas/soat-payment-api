"""Use case for creating a new payment"""

from payment_api.application.commands import FindPaymentByIdCommand
from payment_api.domain.entities import Payment
from payment_api.domain.ports import PaymentRepository


class FindPaymentByIdUseCase:
    """Use case to handle the finding of a payment by its ID"""

    def __init__(self, payment_repository: PaymentRepository):
        self.payment_repository = payment_repository

    async def execute(self, command: FindPaymentByIdCommand) -> Payment:
        """Execute the use case to find a payment by its ID

        :param command: command containing payment ID
        :type command: FindPaymentByIdCommand
        :return: Payment entity corresponding to the given ID
        :rtype: Payment
        :raises NotFound: if payment is not found
        :raises PersistenceError: if there is an error during data retrieval from
            the repository
        """

        payment = await self.payment_repository.find_by_id(id=command.payment_id)
        return payment
