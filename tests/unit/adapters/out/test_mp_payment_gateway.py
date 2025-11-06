# pylint: disable=W0621

"""Unit tests for MPPaymentGateway"""

from datetime import datetime

import pytest
from freezegun import freeze_time
from pytest_mock import MockerFixture

from payment_api.adapters.out.mp_payment_gateway import MPPaymentGateway
from payment_api.domain.entities import PaymentIn, Product
from payment_api.domain.exceptions import PaymentCreationError
from payment_api.domain.value_objects import PaymentStatus
from payment_api.infrastructure.mercado_pago import (
    MercadoPagoAPIClient,
    MPClientError,
    MPCreateOrderIn,
    MPCreateOrderOut,
    MPItem,
)


@pytest.fixture
def mp_settings(mocker: MockerFixture):
    """Fixture to create a mock MercadoPagoSettings"""
    mock_settings = mocker.Mock()
    mock_settings.CALLBACK_URL = "https://example.com/webhook"
    mock_settings.WEBHOOK_KEY = "test-webhook-key"
    return mock_settings


@pytest.fixture
def mp_client(mocker: MockerFixture) -> MercadoPagoAPIClient:
    """Fixture to create a mock MercadoPagoAPIClient"""
    return mocker.Mock(spec=MercadoPagoAPIClient)


@pytest.fixture
def gateway(mp_settings, mp_client: MercadoPagoAPIClient) -> MPPaymentGateway:
    """Fixture to create MPPaymentGateway with mocked dependencies"""
    return MPPaymentGateway(settings=mp_settings, mp_client=mp_client)


@pytest.fixture
def payment_input() -> PaymentIn:
    """Fixture to create sample PaymentIn"""
    return PaymentIn(
        id="A048",
        external_id="empty-A048",
        payment_status=PaymentStatus.OPENED,
        total_order_value=45.0,
        qr_code=None,
        expiration=datetime(2024, 12, 31, 23, 59, 59),
    )


@pytest.fixture
def products() -> list[Product]:
    """Fixture to create sample products list"""
    return [
        Product(
            name="Product 1",
            category="Category A",
            unit_price=10.0,
            quantity=2,
        ),
        Product(
            name="Product 2",
            category="Category B",
            unit_price=25.0,
            quantity=1,
        ),
    ]


@freeze_time("2024-01-01T12:00:00Z")
async def test_should_create_payment_when_mercado_pago_responds_successfully(
    mocker: MockerFixture,
    gateway: MPPaymentGateway,
    mp_client: MercadoPagoAPIClient,
    payment_input: PaymentIn,
    products: list[Product],
):
    """Given a valid payment and products
    When the Mercado Pago API responds successfully
    Then a payment should be created with QR code data
    """

    # Given
    expected_qr_data = "sample-qr-code-data"
    mp_response = MPCreateOrderOut(qr_data=expected_qr_data)
    mp_client.create_dynamic_qr_order = mocker.AsyncMock(return_value=mp_response)

    # When
    result = await gateway.create(payment=payment_input, products=products)

    # Then
    assert result.qr_code == expected_qr_data
    assert result.id == payment_input.id
    assert result.total_order_value == payment_input.total_order_value
    assert result.payment_status == PaymentStatus.OPENED

    # Verify the MP client was called with correct parameters
    mp_client.create_dynamic_qr_order.assert_awaited_once_with(
        order_data=MPCreateOrderIn(
            external_reference=payment_input.id,
            total_amount=payment_input.total_order_value,
            title=f"Order #{payment_input.id}",
            description=f"Order #{payment_input.id}",
            expiration_date="2024-01-01T12:10:00.000+00:00",
            items=[
                MPItem(
                    title="Product 1",
                    category="Category A",
                    quantity=2,
                    unit_measure="unit",
                    unit_price=10.0,
                    total_amount=20.0,
                ),
                MPItem(
                    title="Product 2",
                    category="Category B",
                    quantity=1,
                    unit_measure="unit",
                    unit_price=25.0,
                    total_amount=25.0,
                ),
            ],
            notification_url="https://example.com/webhook?"
            "x-mp-webhook-key=test-webhook-key",
        )
    )


async def test_should_raise_payment_creation_error_when_mercado_pago_fails(
    mocker: MockerFixture,
    gateway: MPPaymentGateway,
    mp_client: MercadoPagoAPIClient,
    payment_input: PaymentIn,
    products: list[Product],
):
    """Given a valid payment and products
    When the Mercado Pago API raises an MPClientError
    Then a PaymentCreationError should be raised
    """

    # Given
    error_message = "Mercado Pago API connection failed"
    mp_client.create_dynamic_qr_order = mocker.AsyncMock(
        side_effect=MPClientError(error_message)
    )

    # When / Then
    with pytest.raises(PaymentCreationError) as exc_info:
        await gateway.create(payment=payment_input, products=products)

    assert f"Failed to create payment in Mercado Pago: {error_message}" in str(
        exc_info.value
    )
    mp_client.create_dynamic_qr_order.assert_awaited_once()
