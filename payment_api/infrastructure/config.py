"""Application configuration module"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    # Pydantic Settings Config
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # General
    PROJECT_NAME: str = "SOAT Tech Challenge Payment Api"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "PRD"
    API_ROOT_PATH: str = "/api"

    # Database
    DB_DSN: str
    DB_ECHO: bool = False

    # HTTP Client
    HTTP_TIMEOUT: float = 10.0  # seconds

    # Mercado Pago Integration
    MERCADO_PAGO_ACCESS_TOKEN: str
    MERCADO_PAGO_USER_ID: str
    MERCADO_PAGO_POS: str
    MERCADO_PAGO_CALLBACK_URL: str

    # Messaging
    SQS_ORDER_CREATED_QUEUE_NAME: str
