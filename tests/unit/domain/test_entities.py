"""Unit tests for Payment entity behaviors"""

from datetime import datetime

from payment_api.domain.entities import PaymentOut
from payment_api.domain.value_objects import PaymentStatus


def test_should_finalize_payment_when_it_is_opened():
    """Given an opened payment
    When finalizing the payment with a valid status
    Then the payment status should be updated accordingly
    """

    # Given
    payment = _get_payment(PaymentStatus.OPENED)

    # When
    updated_payment = payment.finalize(PaymentStatus.CLOSED)

    # Then
    assert updated_payment.payment_status == PaymentStatus.CLOSED
    assert updated_payment is payment


def test_should_not_finalize_when_payment_already_completed():
    """Given a closed payment
    When finalizing the payment
    Then a ValueError should be raised
    """

    # Given
    payment = _get_payment(PaymentStatus.CLOSED)

    # When / Then
    try:
        payment.finalize(PaymentStatus.EXPIRED)
    except ValueError as e:
        assert str(e) == "Unable to update a payment status from CLOSED to EXPIRED"


def test_should_not_allow_reopening_payment():
    """Given an opened payment
    When finalizing the payment with OPENED status
    Then a ValueError should be raised
    """

    # Given
    payment = _get_payment(PaymentStatus.OPENED)

    # When / Then
    try:
        payment.finalize(PaymentStatus.OPENED)
    except ValueError as e:
        assert str(e) == "Unable to update a payment status from OPENED to OPENED"


def _get_payment(status: PaymentStatus) -> PaymentOut:
    return PaymentOut(
        id="A022",
        external_id="ext-1",
        payment_status=status,
        total_order_value=100.0,
        qr_code=None,
        expiration=datetime(2024, 12, 31, 23, 59, 59),
        created_at=datetime(2024, 1, 1, 12, 0, 0),
        timestamp=datetime(2024, 1, 1, 12, 0, 0),
    )
