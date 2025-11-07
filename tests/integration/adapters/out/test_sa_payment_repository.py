# pylint: disable=W0621

"""Test for SQL Alchemy Payment Repository implementation"""

from datetime import datetime

import pytest
from pytest_mock import MockerFixture
from sqlalchemy import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from payment_api.adapters.out.sa_payment_repository import SAPaymentRepository
from payment_api.domain.entities import PaymentIn, PaymentOut
from payment_api.domain.exceptions import NotFound, PersistenceError
from payment_api.domain.value_objects import PaymentStatus
from payment_api.infrastructure.orm.models import Payment as PaymentModel


@pytest.fixture(autouse=True)
async def create_scenario(db_session: AsyncSession):
    """Fixture to create test scenario before each test"""
    payments = [
        {
            "id": "A001",
            "external_id": "empty-A001",
            "payment_status": PaymentStatus.OPENED,
            "total_order_value": 100.0,
            "qr_code": "qr-A001",
            "expiration": datetime(2023, 1, 1, 0, 10, 0),
            "created_at": datetime(2023, 1, 1, 0, 0, 0),
            "timestamp": datetime(2023, 1, 1, 0, 0, 0),
        }
    ]

    await db_session.execute(insert(PaymentModel), payments)
    await db_session.commit()


@pytest.fixture
def repository(db_session: AsyncSession) -> SAPaymentRepository:
    """Fixture to create an instance of SAPaymentRepository"""
    return SAPaymentRepository(session=db_session)


async def test_should_return_payment_by_id(
    repository: SAPaymentRepository,
):
    """Given a payment id
    When calling the repository to get the payment by id
    Then the payment with the given id should be returned in domain format
    """

    # Given
    payment_id = "A001"

    # When
    payment = await repository.find_by_id(payment_id=payment_id)

    # Then
    assert payment == PaymentOut(
        id="A001",
        external_id="empty-A001",
        payment_status=PaymentStatus.OPENED,
        total_order_value=100.0,
        qr_code="qr-A001",
        expiration="2023-01-01T00:10:00",
        created_at="2023-01-01T00:00:00",
        timestamp="2023-01-01T00:00:00",
    )


async def test_should_raise_not_found_when_payment_id_does_not_exist(
    repository: SAPaymentRepository,
):
    """Given a non-existing payment id
    When calling the repository to get the payment by id
    Then a NotFound exception should be raised
    """

    # Given
    payment_id = "NON_EXISTING_ID"

    # When / Then
    with pytest.raises(NotFound) as exc_info:
        await repository.find_by_id(payment_id=payment_id)

    assert str(exc_info.value) == f"No payment found with ID: {payment_id}"


async def test_should_raise_persistence_error_on_db_issue(
    mocker: MockerFixture,
    repository: SAPaymentRepository,
):
    """Given a payment id
    When there is a database issue while fetching the payment
    Then a PersistenceError should be raised
    """

    # Given
    payment_id = "A001"

    async def raise_sqlalchemy_error(*args, **kwargs):
        raise SQLAlchemyError("Simulated database error")

    mocker.patch.object(
        repository.session,
        "execute",
        side_effect=raise_sqlalchemy_error,
    )

    # When / Then
    with pytest.raises(PersistenceError) as exc_info:
        await repository.find_by_id(payment_id=payment_id)

    assert "Simulated database error" in str(exc_info.value)


async def test_should_return_true_when_payment_exists_by_id(
    repository: SAPaymentRepository,
):
    """Given an existing payment id
    When calling the repository to check if payment exists by id
    Then True should be returned
    """

    # Given
    payment_id = "A001"

    # When
    exists = await repository.exists_by_id(payment_id=payment_id)

    # Then
    assert exists is True


async def test_should_return_false_when_payment_does_not_exist_by_id(
    repository: SAPaymentRepository,
):
    """Given a non-existing payment id
    When calling the repository to check if payment exists by id
    Then False should be returned
    """

    # Given
    payment_id = "NON_EXISTING_ID"

    # When
    exists = await repository.exists_by_id(payment_id=payment_id)

    # Then
    assert exists is False


async def test_should_raise_persistence_error_on_exists_by_id_db_issue(
    mocker: MockerFixture,
    repository: SAPaymentRepository,
):
    """Given a payment id
    When there is a database issue while checking if payment exists by id
    Then a PersistenceError should be raised
    """

    # Given
    payment_id = "A001"

    mocker.patch.object(
        repository.session,
        "execute",
        side_effect=SQLAlchemyError("Simulated database error"),
    )

    # When / Then
    with pytest.raises(PersistenceError) as exc_info:
        await repository.exists_by_id(payment_id=payment_id)

    assert "Simulated database error" in str(exc_info.value)


async def test_should_return_true_when_payment_exists_by_external_id(
    repository: SAPaymentRepository,
):
    """Given an existing payment external id
    When calling the repository to check if payment exists by external id
    Then True should be returned
    """

    # Given
    external_id = "empty-A001"

    # When
    exists = await repository.exists_by_external_id(external_id=external_id)

    # Then
    assert exists is True


async def test_should_return_false_when_payment_does_not_exist_by_external_id(
    repository: SAPaymentRepository,
):
    """Given a non-existing payment external id
    When calling the repository to check if payment exists by external id
    Then False should be returned
    """

    # Given
    external_id = "NON_EXISTING_EXTERNAL_ID"

    # When
    exists = await repository.exists_by_external_id(external_id=external_id)

    # Then
    assert exists is False


async def test_should_raise_persistence_error_on_exists_by_external_id_db_issue(
    mocker: MockerFixture,
    repository: SAPaymentRepository,
):
    """Given a payment external id
    When there is a database issue while checking if payment exists by external id
    Then a PersistenceError should be raised
    """

    # Given
    external_id = "empty-A001"

    mocker.patch.object(
        repository.session,
        "execute",
        side_effect=SQLAlchemyError("Simulated database error"),
    )

    # When / Then
    with pytest.raises(PersistenceError) as exc_info:
        await repository.exists_by_external_id(external_id=external_id)

    assert "Simulated database error" in str(exc_info.value)


async def test_should_insert_new_payment_when_payment_does_not_exist(
    repository: SAPaymentRepository,
):
    """Given a new payment
    When calling the repository to save the payment
    Then the payment should be inserted and returned
    """

    # Given
    payment = PaymentIn(
        id="B001",
        external_id="external-B001",
        payment_status=PaymentStatus.OPENED,
        total_order_value=200.0,
        qr_code="qr-B001",
        expiration=datetime(2023, 1, 1, 0, 15, 0),
    )

    # When
    saved_payment = await repository.save(payment=payment)

    # Then
    assert saved_payment.id == "B001"
    assert saved_payment.external_id == "external-B001"
    assert saved_payment.payment_status == PaymentStatus.OPENED
    assert saved_payment.total_order_value == 200.0
    assert saved_payment.qr_code == "qr-B001"
    assert saved_payment.expiration == datetime(2023, 1, 1, 0, 15, 0)


async def test_should_update_existing_payment_when_payment_exists(
    repository: SAPaymentRepository,
):
    """Given an existing payment with updated data
    When calling the repository to save the payment
    Then the payment should be updated and returned
    """

    # Given
    payment = PaymentIn(
        id="A001",
        external_id="updated-A001",
        payment_status=PaymentStatus.CLOSED,
        total_order_value=150.0,
        qr_code="qr-A001-updated",
        expiration=datetime(2023, 1, 1, 0, 20, 0),
    )

    # When
    saved_payment = await repository.save(payment=payment)

    # Then
    assert saved_payment.id == "A001"
    assert saved_payment.external_id == "updated-A001"
    assert saved_payment.payment_status == PaymentStatus.CLOSED
    assert saved_payment.total_order_value == 150.0
    assert saved_payment.qr_code == "qr-A001-updated"
    assert saved_payment.expiration == datetime(2023, 1, 1, 0, 20, 0)


async def test_should_raise_persistence_error_on_insert_db_issue(
    mocker: MockerFixture,
    repository: SAPaymentRepository,
):
    """Given a new payment
    When there is a database issue during insert operation
    Then a PersistenceError should be raised
    """

    # Given
    payment = PaymentIn(
        id="C001",
        external_id="external-C001",
        payment_status=PaymentStatus.OPENED,
        total_order_value=300.0,
        qr_code="qr-C001",
        expiration=datetime(2023, 1, 1, 0, 25, 0),
    )

    # Mock exists_by_id to return False (so it tries to insert)
    mocker.patch.object(repository, "exists_by_id", return_value=False)
    mocker.patch.object(
        repository.session,
        "execute",
        side_effect=SQLAlchemyError("Insert constraint violation"),
    )

    # When / Then
    with pytest.raises(PersistenceError) as exc_info:
        await repository.save(payment=payment)

    assert "Insert constraint violation" in str(exc_info.value)


async def test_should_raise_persistence_error_on_update_db_issue(
    mocker: MockerFixture,
    repository: SAPaymentRepository,
):
    """Given an existing payment
    When there is a database issue during update operation
    Then a PersistenceError should be raised
    """

    # Given
    payment = PaymentIn(
        id="A001",
        external_id="updated-A001",
        payment_status=PaymentStatus.CLOSED,
        total_order_value=150.0,
        qr_code="qr-A001-updated",
        expiration=datetime(2023, 1, 1, 0, 20, 0),
    )

    # Mock exists_by_id to return True (so it tries to update)
    mocker.patch.object(repository, "exists_by_id", return_value=True)
    mocker.patch.object(
        repository.session,
        "execute",
        side_effect=SQLAlchemyError("Update constraint violation"),
    )

    # When / Then
    with pytest.raises(PersistenceError) as exc_info:
        await repository.save(payment=payment)

    assert "Update constraint violation" in str(exc_info.value)
