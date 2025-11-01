"""Entrypoint module for the Payment API application"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from payment_api.adapters.inbound.rest.v1 import payment_router_v1
from payment_api.infrastructure import factory
from payment_api.infrastructure.config import (
    APPSettings,
    AWSSettings,
    DatabaseSettings,
    HTTPClientSettings,
    MercadoPagoSettings,
    PaymentClosedPublisherSettings,
)

logger = logging.getLogger(__name__)


def create_api() -> FastAPI:
    """Create FastAPI application instance"""

    logger.info("Creating FastAPI application instance")
    app_instance = FastAPI(lifespan=fastapi_lifespan)
    logger.info("Including payment router v1")
    app_instance.include_router(payment_router_v1)
    return app_instance


@asynccontextmanager
async def fastapi_lifespan(app_instance: FastAPI):
    """Lifespan context manager for FastAPI application"""

    # Application state setup
    logger.info("Loading application settings")
    app_instance.state.app_settings = APPSettings()
    logger.info("Loading database settings")
    app_instance.state.database_settings = DatabaseSettings()
    logger.info("Loading HTTP client settings")
    app_instance.state.http_client_settings = HTTPClientSettings()
    logger.info("Loading MercadoPago settings")
    app_instance.state.mercado_pago_settings = MercadoPagoSettings()
    logger.info("Loading AWS settings")
    app_instance.state.aws_settings = AWSSettings()
    logger.info("Loading PaymentClosedPublisher settings")
    app_instance.state.payment_closed_publisher_settings = (
        PaymentClosedPublisherSettings()
    )

    app_instance.title = app_instance.state.app_settings.TITLE
    app_instance.version = app_instance.state.app_settings.VERSION
    app_instance.root_path = app_instance.state.app_settings.ROOT_PATH
    logger.info(
        "Application settings loaded title=%s version=%s root_path=%s",
        app_instance.title,
        app_instance.version,
        app_instance.root_path,
    )

    logger.info("Starting session manager")
    app_instance.state.session_manager = factory.get_session_manager(
        settings=app_instance.state.database_settings
    )

    logger.info("Starting HTTP client")
    app_instance.state.http_client = factory.get_http_client(
        settings=app_instance.state.http_client_settings
    )

    # Application state teardown
    yield
    logger.info("Closing session manager")
    await app_instance.state.session_manager.close()
    logger.info("Closing HTTP client")
    await app_instance.state.http_client.aclose()


app = create_api()
