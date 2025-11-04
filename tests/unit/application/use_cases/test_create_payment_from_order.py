# pylint: disable=W0621

"""Unit tests for CreatePaymentFromOrderUseCase"""

import pytest
from freezegun import freeze_time
from pytest_mock import MockerFixture

from payment_api.application.commands import CreatePaymentFromOrderCommand, ProductDTO
from payment_api.application.use_cases import CreatePaymentFromOrderUseCase
from payment_api.domain.entities import PaymentIn, PaymentOut, Product
from payment_api.domain.exceptions import PaymentCreationError
from payment_api.domain.value_objects import PaymentStatus


@pytest.fixture
def use_case(mocker: MockerFixture) -> CreatePaymentFromOrderUseCase:
    """Fixture to create an instance of CreatePaymentFromOrderUseCase with mocked
    dependencies
    """
    payment_repository = mocker.Mock()
    payment_gateway = mocker.Mock()
    return CreatePaymentFromOrderUseCase(
        payment_repository=payment_repository,
        payment_gateway=payment_gateway,
    )


@pytest.fixture
def command() -> CreatePaymentFromOrderCommand:
    """Fixture to create a sample CreatePaymentFromOrderCommand"""
    return CreatePaymentFromOrderCommand(
        order_id="A048",
        total_order_value=45.0,
        products=[
            ProductDTO(
                name="Product 1", category="Category A", unit_price=10.0, quantity=2
            ),
            ProductDTO(
                name="Product 2", category="Category B", unit_price=15.0, quantity=1
            ),
        ],
    )


@freeze_time("2024-01-01T12:00:00Z")
async def test_should_create_payment_from_order_when_it_does_not_exist(
    mocker: MockerFixture,
    use_case: CreatePaymentFromOrderUseCase,
    command: CreatePaymentFromOrderCommand,
):
    """Given a valid command to create a payment from an order
    When executing the use case and the payment does not already exist
    Then a new payment should be created and returned
    """

    # Given
    payment_in_mock = PaymentIn(
        id="A048",
        external_id="empty-A048",
        payment_status=PaymentStatus.OPENED,
        total_order_value=45.0,
        qr_code=None,
        expiration="2024-01-01T12:15:00",
    )

    payment_out_mock = PaymentOut.model_validate(
        {
            **payment_in_mock.model_dump(),
            "created_at": "2024-01-01T12:00:00",
            "timestamp": "2024-01-01T12:00:00",
        }
    )
    use_case.payment_repository.exists_by_id = mocker.AsyncMock(return_value=False)
    use_case.payment_gateway.create = mocker.AsyncMock(return_value=payment_in_mock)
    use_case.payment_repository.save = mocker.AsyncMock(return_value=payment_out_mock)

    # When
    created_payment = await use_case.execute(command=command)

    # Then
    assert created_payment.id == command.order_id
    assert created_payment.payment_status == PaymentStatus.OPENED
    use_case.payment_repository.exists_by_id.assert_awaited_once_with(
        payment_id=command.order_id
    )

    use_case.payment_gateway.create.assert_awaited_once_with(
        payment=payment_in_mock,
        products=[Product.model_validate(p.model_dump()) for p in command.products],
    )

    use_case.payment_repository.save.assert_awaited_once_with(payment=payment_in_mock)


async def test_should_not_create_payment_when_it_already_exists(
    mocker: MockerFixture,
    use_case: CreatePaymentFromOrderUseCase,
    command: CreatePaymentFromOrderCommand,
):
    """Given a valid command to create a payment from an order
    When executing the use case and the payment already exists
    Then a PaymentCreationError should be raised
    """

    # Given
    use_case.payment_repository.exists_by_id = mocker.AsyncMock(return_value=True)
    use_case.payment_gateway.create = mocker.AsyncMock()
    use_case.payment_repository.save = mocker.AsyncMock()

    # When / Then
    with pytest.raises(PaymentCreationError) as exc_info:
        await use_case.execute(command=command)

    assert str(exc_info.value) == f"Payment with ID {command.order_id} already exists"
    use_case.payment_repository.exists_by_id.assert_awaited_once_with(
        payment_id=command.order_id
    )

    use_case.payment_repository.exists_by_id.assert_awaited_once_with(
        payment_id=command.order_id
    )

    use_case.payment_gateway.create.assert_not_awaited()
    use_case.payment_repository.save.assert_not_awaited()
