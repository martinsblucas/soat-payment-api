"""Module with authentication dependencies for the REST API"""

import logging
from typing import Annotated

from fastapi import HTTPException, Query, Request

logger = logging.getLogger(__name__)


def validate_mercado_pago_notification(
    key: Annotated[str, Query(alias="x-mp-webhook-key")],
    request: Request,
):
    """Validate Mercado Pago notification using webhook key"""

    if key != request.app.state.mercado_pago_settings.WEBHOOK_KEY:
        logger.warning("Invalid Mercado Pago webhook key")
        raise HTTPException(status_code=401, detail="Unauthorized")
