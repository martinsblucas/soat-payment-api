"""Schemas for Mercado Pago integration in the payment API."""

from enum import Enum, unique

from pydantic import BaseModel, Field


@unique
class MPOrderStatus(str, Enum):
    """Enumeration of possible order statuses in Mercado Pago."""

    OPENED = "opened"
    CLOSED = "closed"
    EXPIRED = "expired"


class MPItem(BaseModel):
    """Schema representing an item in Mercado Pago."""

    title: str = Field(..., description="Title of the item.")
    category: str = Field(..., description="Category of the item.")
    quantity: int = Field(..., description="Quantity of the item.")
    unit_measure: str = Field(..., description="Unit measure of the item.")
    unit_price: float = Field(..., description="Unit price of the item.")
    total_amount: float = Field(..., description="Total amount for the item.")


class MPCreateOrderIn(BaseModel):
    """Schema for creating an order in Mercado Pago."""

    external_reference: str = Field(
        ..., description="External reference for the order."
    )

    total_amount: float = Field(..., description="Total amount for the order.")
    title: str = Field(..., description="Title of the order.")
    description: str = Field(..., description="Description of the order.")
    expiration_date: str = Field(..., description="Expiration date of the order.")
    items: list[MPItem] = Field(..., description="List of items in the order.")
    notification_url: str = Field(
        ..., description="Webhook notification URL to receive updates about the order."
    )


class MPCreateOrderOut(BaseModel):
    """Schema for the response after creating an order in Mercado Pago."""

    qr_data: str = Field(..., description="QR code data for the order.")


class MPOrder(BaseModel):
    """Schema representing an order in Mercado Pago."""

    id: int = Field(..., description="Unique identifier for the order.")
    status: MPOrderStatus = Field(..., description="Status of the order.")
    external_reference: str = Field(
        ..., description="External reference for the order."
    )


class MPPayment(BaseModel):
    """Schema representing a payment in Mercado Pago."""
