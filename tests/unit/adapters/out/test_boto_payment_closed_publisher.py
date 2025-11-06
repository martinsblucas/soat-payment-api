# pylint: disable=W0621

"""Unit tests for BotoPaymentClosedPublisher"""

import pytest
from botocore.exceptions import ClientError as BotoCoreClientError
from pytest_mock import MockerFixture

from payment_api.adapters.out.boto_payment_closed_publisher import (
    BotoPaymentClosedPublisher,
)
from payment_api.domain.events import PaymentClosedEvent
from payment_api.domain.exceptions import EventPublishingError


@pytest.fixture
def publisher_settings(mocker: MockerFixture):
    """Fixture to create a mock PaymentClosedPublisherSettings"""
    mock_settings = mocker.Mock()
    mock_settings.TOPIC_ARN = "arn:aws:sns:us-east-1:123456789012:payment-closed-topic"
    mock_settings.GROUP_ID = "payment-closed-group"
    return mock_settings


@pytest.fixture
def aio_boto3_session(mocker: MockerFixture):
    """Fixture to create a mock AIOBoto3Session"""
    return mocker.Mock()


@pytest.fixture
def publisher(aio_boto3_session, publisher_settings) -> BotoPaymentClosedPublisher:
    """Fixture to create BotoPaymentClosedPublisher with mocked dependencies"""
    return BotoPaymentClosedPublisher(
        aio_boto3_session=aio_boto3_session, settings=publisher_settings
    )


@pytest.fixture
def payment_closed_event() -> PaymentClosedEvent:
    """Fixture to create sample PaymentClosedEvent"""
    return PaymentClosedEvent(payment_id="A048")


async def test_should_publish_event_when_sns_responds_successfully(
    mocker: MockerFixture,
    publisher: BotoPaymentClosedPublisher,
    aio_boto3_session,
    payment_closed_event: PaymentClosedEvent,
):
    """Given a valid payment closed event
    When the AWS SNS responds successfully
    Then the event should be published to the SNS topic
    """

    # Given
    expected_message_id = "12345678-1234-1234-1234-123456789012"
    mock_sns_resource = mocker.AsyncMock()
    mock_topic = mocker.AsyncMock()
    mock_topic.arn = "arn:aws:sns:us-east-1:123456789012:payment-closed-topic"
    mock_topic.publish = mocker.AsyncMock(
        return_value={"MessageId": expected_message_id}
    )

    # Configure the async context manager for SNS resource
    aio_boto3_session.resource.return_value.__aenter__ = mocker.AsyncMock(
        return_value=mock_sns_resource
    )
    aio_boto3_session.resource.return_value.__aexit__ = mocker.AsyncMock(
        return_value=None
    )

    # Configure SNS resource to return the topic
    mock_sns_resource.Topic.return_value = mock_topic

    # When
    await publisher.publish(event=payment_closed_event)

    # Then
    # Verify SNS resource was created correctly
    aio_boto3_session.resource.assert_called_once_with("sns")

    # Verify Topic was created with correct ARN
    mock_sns_resource.Topic.assert_called_once_with(
        "arn:aws:sns:us-east-1:123456789012:payment-closed-topic"
    )

    # Verify publish was called with correct parameters
    mock_topic.publish.assert_awaited_once_with(
        Subject="payment-closed",
        Message=payment_closed_event.model_dump_json(),
        MessageGroupId="payment-closed-group",
        MessageDeduplicationId=str(payment_closed_event.id),
    )


async def test_should_raise_event_publishing_error_when_sns_fails(
    mocker: MockerFixture,
    publisher: BotoPaymentClosedPublisher,
    aio_boto3_session,
    payment_closed_event: PaymentClosedEvent,
):
    """Given a valid payment closed event
    When the AWS SNS raises a BotoCoreClientError
    Then an EventPublishingError should be raised
    """

    # Given
    error_message = "Access denied to SNS topic"
    mock_sns_resource = mocker.AsyncMock()
    mock_topic = mocker.AsyncMock()
    mock_topic.publish = mocker.AsyncMock(
        side_effect=BotoCoreClientError(
            error_response={
                "Error": {"Code": "AccessDenied", "Message": error_message}
            },
            operation_name="Publish",
        )
    )

    # Configure the async context manager for SNS resource
    aio_boto3_session.resource.return_value.__aenter__ = mocker.AsyncMock(
        return_value=mock_sns_resource
    )
    aio_boto3_session.resource.return_value.__aexit__ = mocker.AsyncMock(
        return_value=None
    )

    # Configure SNS resource to return the topic
    mock_sns_resource.Topic.return_value = mock_topic

    # When / Then
    with pytest.raises(EventPublishingError) as exc_info:
        await publisher.publish(event=payment_closed_event)

    assert str(exc_info.value) == "Error publishing message to SNS topic"

    # Verify the publish method was called before failing
    mock_topic.publish.assert_awaited_once_with(
        Subject="payment-closed",
        Message=payment_closed_event.model_dump_json(),
        MessageGroupId="payment-closed-group",
        MessageDeduplicationId=str(payment_closed_event.id),
    )
