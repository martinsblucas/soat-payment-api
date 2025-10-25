from pydantic import BaseModel, Field


class FinalizePaymentByMercadoPagoPaymentIdCommand(BaseModel):
    """Command to finalize a payment using Mercado Pago payment ID."""

    payment_id: str = Field(..., description="The ID of the payment to finalize")
