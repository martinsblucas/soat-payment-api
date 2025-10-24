"""Factory module for manual dependency injection"""

from payment_api.config import Settings


def get_settings() -> Settings:
    """Return a Settings instance"""
    return Settings()
