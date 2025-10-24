"""Product entity module"""

from pydantic import BaseModel, Field


class Product(BaseModel):
    """Product entity to be sent to the payment gateway."""

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
