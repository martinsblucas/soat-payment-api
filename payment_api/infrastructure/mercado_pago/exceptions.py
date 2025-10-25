"""Custom exceptions for Mercado Pago API errors."""


class MPClientError(Exception):
    """Base exception for Mercado Pago client errors."""


class MPNotFoundError(MPClientError):
    """Exception raised when a Mercado Pago resource is not found."""
