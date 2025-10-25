"""Use case for creating a new payment"""

from datetime import datetime, timedelta

from payment_api.application.commands import CreatePaymentFromOrderCommand
from payment_api.domain.entities import Payment, Product
from payment_api.domain.exceptions import PaymentCreationError
from payment_api.domain.ports import PaymentGateway, PaymentRepository
from payment_api.domain.value_objects import PaymentStatus


class CreatePaymentFromOrderUseCase:
    """Use case to handle the creation of a new payment based on an order"""

    def __init__(
        self,
        payment_repository: PaymentRepository,
        payment_gateway: PaymentGateway,
    ):
        self.payment_repository = payment_repository
        self.payment_gateway = payment_gateway

    async def execute(self, command: CreatePaymentFromOrderCommand) -> Payment:
        """Execute the use case to create a new payment

        :param command: command containing the details for payment creation
        :type command: CreatePaymentFromOrderCommand
        :return: Payment entity representing the created payment
        :rtype: Payment
        :raises PaymentCreationError: if there is an error during payment creation
        :raises PersistenceError: if there is an error during data persistence to
            the repository
        """

        # validate
        if await self.payment_repository.exists_by_id(id=command.order_id):
            raise PaymentCreationError(
                f"Payment with ID {command.order_id} already exists"
            )

        # convert ProductDTOs to Products
        products = [Product.model_validate(product) for product in command.products]

        # create payment entity
        expiration = datetime.now() + timedelta(minutes=15)
        payment = Payment(
            id=command.order_id,
            external_id=f"empty-{command.order_id}",
            payment_status=PaymentStatus.OPENED,
            total_order_value=command.total_order_value,
            products=products,
            expiration=expiration,
        )

        # create payment in gateway
        try:
            payment = await self.payment_gateway.create(
                payment=payment, products=products
            )
        except Exception as e:
            raise PaymentCreationError(
                f"Error creating payment in gateway: {str(e)}"
            ) from e

        # save payment in repository
        return await self.payment_repository.save(payment=payment)
