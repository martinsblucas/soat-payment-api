"""SQL Alchemy implementation of the PaymentRepository port"""

from sqlalchemy import exists, insert, select, update
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from payment_api.domain.entities import PaymentIn, PaymentOut
from payment_api.domain.exceptions import NotFound, PersistenceError
from payment_api.domain.ports import PaymentRepository
from payment_api.infrastructure.orm.models import Payment as PaymentModel


class SAPaymentRepository(PaymentRepository):
    """A SQL Alchemy implementation of the PaymentRepository port"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_id(self, payment_id: str) -> PaymentOut:
        try:
            result = await self.session.execute(
                select(PaymentModel).where(PaymentModel.id == payment_id)
            )

            return PaymentOut.model_validate(result.scalars().one())

        except NoResultFound as error:
            raise NotFound(f"No payment found with ID: {payment_id}") from error

        except SQLAlchemyError as error:
            raise PersistenceError(
                f"Error finding payment by ID {payment_id}: {str(error)}"
            ) from error

    async def exists_by_id(self, payment_id: str) -> bool:
        try:
            result = await self.session.execute(
                select(exists().where(PaymentModel.id == payment_id))
            )

            return result.scalar()

        except SQLAlchemyError as error:
            raise PersistenceError(
                f"Error checking payment existence by ID {payment_id}: {str(error)}"
            ) from error

    async def exists_by_external_id(self, external_id: str) -> bool:
        try:
            result = await self.session.execute(
                select(exists().where(PaymentModel.external_id == external_id))
            )

            return result.scalar()

        except SQLAlchemyError as error:
            raise PersistenceError(
                f"Error checking payment existence by external ID {external_id}:"
                f"{str(error)}"
            ) from error

    async def save(self, payment: PaymentIn) -> PaymentOut:
        """Save a payment into the repository
        :param payment: Payment to be saved
        :type payment: PaymentIn
        :return: Saved Payment
        :rtype: PaymentOut
        """

        if await self.exists_by_id(payment_id=payment.id):
            return await self._update(payment=payment)
        return await self._insert(payment=payment)

    async def _insert(self, payment: PaymentIn) -> PaymentOut:
        """Insert a new payment into the repository

        :param payment: Payment to be inserted
        :type payment: PaymentIn
        :return: Inserted Payment
        :rtype: PaymentOut
        """
        try:
            result = await self.session.execute(
                insert(PaymentModel)
                .values(**payment.model_dump())
                .returning(PaymentModel)
            )

            inserted_payment = PaymentOut.model_validate(result.scalars().one())
            await self.session.commit()
            return inserted_payment

        except SQLAlchemyError as error:
            raise PersistenceError(
                f"Error inserting payment {payment.id}: {str(error)}"
            ) from error

    async def _update(self, payment: PaymentIn) -> PaymentOut:
        """Update an existing payment in the repository

        :param payment: Payment to be updated
        :type payment: PaymentIn
        :return: Updated Payment
        :rtype: PaymentOut
        """
        try:
            result = await self.session.execute(
                update(PaymentModel)
                .where(PaymentModel.id == payment.id)
                .values(**payment.model_dump())
                .returning(PaymentModel)
            )

            updated_payment = PaymentOut.model_validate(result.scalars().one())
            await self.session.commit()
            return updated_payment

        except SQLAlchemyError as error:
            raise PersistenceError(
                f"Error updating payment {payment.id}: {str(error)}"
            ) from error
