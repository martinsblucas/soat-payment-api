"""Module defining the command to find a payment by its ID"""

from pydantic import BaseModel, Field


class FindPaymentByIdCommand(BaseModel):
    """Command to find a payment by its ID"""

    payment_id: str = Field(..., description="Unique identifier for the payment")
