"""Module defining the CreatePaymentCommand for creating payments"""

from pydantic import BaseModel, Field


class ProductDTO(BaseModel):
    """Product entity to be used by the CreatePaymentFromOrderCommand."""

    name: str = Field(description="Name of the product")
    category: str = Field(description="Category of the product")
    unit_price: float = Field(description="Unit price of the product")
    quantity: int = Field(description="Quantity of the product")

    def get_total_value(self) -> float:
        """Calculate total value of the product.

        :rtype: float
        :return: Total value of the product.
        """
        return self.unit_price * self.quantity


class CreatePaymentFromOrderCommand(BaseModel):
    """Command to create a new payment"""

    order_id: str = Field(..., description="Unique identifier for the order")
    total_order_value: float = Field(..., description="Total value of the order")
    products: list[ProductDTO] = Field(
        ..., description="List of products associated with the payment"
    )
