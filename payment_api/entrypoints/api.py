"""Entrypoint module for the Payment API application"""

from payment_api.infrastructure.factory import create_api

app = create_api()
