import logging
import asyncio

from src.redis import add_prices
from src.parser import parse_portal_data
from src.bot import redis
from src.notify import compare_and_notify


async def fill_db_and_notify() -> None:
    """Fill db and notify users if price changed."""
    data = parse_portal_data()

    try:
        await add_prices(data, redis)
    except Exception as e:
        logging.error(f"Error while filling db: {e}")

    await compare_and_notify(data)

    # TODO: check if notification was sent already


if __name__ == '__main__':
    asyncio.run(fill_db_and_notify())
