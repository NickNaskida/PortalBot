import json
import logging
import asyncio

from src.redis import add_prices, get_yesterday_prices, get_subscribed_users
from src.parser import parse_portal_data
from src.bot import redis
from src.utils import format_prices, format_price
from src.notify import send_notification


async def fill_db_and_notify() -> None:
    """Fill db and notify users if price changed."""
    data = parse_portal_data()

    try:
        await add_prices(data, redis)
    except Exception as e:
        logging.error(f"Error while filling db: {e}")

    yesterday_prices = await get_yesterday_prices(redis)
    change = False

    if yesterday_prices:
        yesterday_prices = json.loads(yesterday_prices)

        for fuel, price in data.items():
            yesterday_price = yesterday_prices.get(fuel)
            if price < yesterday_price:
                data[fuel] = f"{price} ↓ ({format_price(float(yesterday_price) - float(price))})"
                change = True
            elif price > yesterday_price:
                data[fuel] = f"{price} ↑ ({format_price(float(yesterday_price) - float(price))})"

        if change:
            yesterday_prices = format_prices(yesterday_prices)
            data = format_prices(data)
            message = f"დაფიქსირდა ფასების ცვლილება:\n\nძველი ფასები:\n\n{yesterday_prices}\n\nახალი ფასები:\n\n{data}"
            subscribers = await get_subscribed_users(redis)

            for user in subscribers:
                print(f"Sending notification to {user}...")
                await send_notification(user, message)
                await asyncio.sleep(.05)


if __name__ == '__main__':
    asyncio.run(fill_db_and_notify())
