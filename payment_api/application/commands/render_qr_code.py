"""Command to render a QR code for a payment"""

from pydantic import BaseModel, Field


class RenderQRCodeCommand(BaseModel):
    """Command to render a QR code for a payment"""

    payment_id: str = Field(..., description="The unique identifier of the payment")
