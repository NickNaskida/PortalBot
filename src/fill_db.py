import logging
import asyncio

from src.redis import add_prices
from src.parser import parse_portal_data
from src.bot import redis


async def fill_db():
    data = parse_portal_data()

    try:
        await add_prices(data, redis)
    except Exception as e:
        logging.error(f"Error while filling db: {e}")


if __name__ == '__main__':
    asyncio.run(fill_db())
