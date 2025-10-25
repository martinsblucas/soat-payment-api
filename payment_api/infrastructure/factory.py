"""Factory module for manual dependency injection"""

from typing import AsyncIterator

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from payment_api.adapters.out import MPPaymentGateway, SAPaymentRepository
from payment_api.domain.ports import PaymentGateway, PaymentRepository
from payment_api.infrastructure.config import Settings
from payment_api.infrastructure.mercado_pago import MercadoPagoAPIClient
from payment_api.infrastructure.orm import SessionManager


def get_settings() -> Settings:
    """Return a Settings instance"""
    return Settings()


def get_session_manager(settings: Settings) -> SessionManager:
    """Return a SessionManager instance"""
    return SessionManager(
        host=settings.DB_DSN, engine_kwargs={"echo": settings.DB_ECHO}
    )


async def get_db_session(
    session_manager: SessionManager,
) -> AsyncIterator[AsyncSession]:
    """Get a database session"""
    async with session_manager.session() as session:
        yield session


def get_http_client(settings: Settings) -> AsyncClient:
    """Return an AsyncClient instance"""
    return AsyncClient(timeout=settings.HTTP_TIMEOUT)


def get_payment_repository(session: AsyncSession) -> PaymentRepository:
    """Return a PaymentRepository instance"""
    return SAPaymentRepository(session=session)


def get_mercado_pago_client(
    settings: Settings, http_client: AsyncClient
) -> MercadoPagoAPIClient:
    """Return a MercadoPagoAPIClient instance"""
    return MercadoPagoAPIClient(settings=settings, http_client=http_client)


def get_payment_gateway(
    settings: Settings, mp_client: MercadoPagoAPIClient
) -> PaymentGateway:
    """Return a MPPaymentGateway instance"""
    return MPPaymentGateway(settings=settings, mp_client=mp_client)
