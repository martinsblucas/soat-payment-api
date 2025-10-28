"""Order created event listener entrypoint module"""

import asyncio

from payment_api.infrastructure.factory import (
    create_order_created_listener,
    get_create_payment_from_order_use_case,
    get_db_session,
    get_http_client,
    get_mercado_pago_api_client,
    get_payment_gateway,
    get_payment_repository,
    get_session_manager,
    get_settings,
)


async def main():
    """Run the order created event listener"""

    try:
        settings = get_settings()
        session_manager = get_session_manager(settings=settings)
        http_client = get_http_client(settings=settings)
        db_session = await anext(get_db_session(session_manager=session_manager))
        repository = get_payment_repository(session=db_session)
        mp_api_client = get_mercado_pago_api_client(
            settings=settings, http_client=http_client
        )

        gateway = get_payment_gateway(
            settings=settings,
            mp_client=mp_api_client,
        )

        create_payment_from_order_use_case = get_create_payment_from_order_use_case(
            payment_repository=repository,
            payment_gateway=gateway,
        )

        listener = create_order_created_listener(
            session=db_session,
            use_case=create_payment_from_order_use_case,
            settings=settings,
        )

        await listener.listen()
    finally:
        await session_manager.close()
        await http_client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
