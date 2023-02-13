import json
import logging

import asyncio
from aiogram import exceptions

from src.config import bot
from src.redis import (
    get_yesterday_prices,
    get_subscribed_users,
    get_notified_users,
    add_notified_user
)
from src.bot import redis
from src.utils import format_prices, format_price


async def send_notification(user_id, message) -> None:
    try:
        await bot.send_message(user_id, message, parse_mode="Markdown")
    except exceptions.BotBlocked:
        logging.error(f"Target [ID:{user_id}]: blocked by user")
    except exceptions.ChatNotFound:
        logging.error(f"Target [ID:{user_id}]: invalid user ID")
    except exceptions.RetryAfter as e:
        logging.error(
            f"Target [ID:{user_id}]: Flood limit is exceeded. "
            f"Sleep {e.timeout} seconds."
        )
        await asyncio.sleep(e.timeout)
        return await bot.send_message(user_id, message, parse_mode="Markdown")  # Recursive call
    except exceptions.UserDeactivated:
        logging.error(f"Target [ID:{user_id}]: user is deactivated")
    except exceptions.TelegramAPIError:
        logging.exception(f"Target [ID:{user_id}]: failed")
    else:
        logging.info(f"Target [ID:{user_id}]: success")


async def compare_and_notify(data):
    yesterday_prices = await get_yesterday_prices(redis)
    formatted_data = {}
    change = False

    if yesterday_prices:
        yesterday_prices = json.loads(yesterday_prices)

        for fuel, price in data.items():
            yesterday_price = yesterday_prices.get(fuel)

            if price != yesterday_price:
                change = True

            if price < yesterday_price:
                formatted_data[fuel] = f"{price} ・↓({format_price(float(yesterday_price) - float(price))})"
            elif price > yesterday_price:
                formatted_data[fuel] = f"{price} ・↑({format_price(float(yesterday_price) - float(price))})"

        if not change:
            return

        formatted_data = format_prices(formatted_data)
        message = f"🚨💬 დაფიქსირდა ფასების ცვლილება:\n\n{formatted_data}"
        subscribers = await get_subscribed_users(redis)

        for user in subscribers:
            notified_users = await get_notified_users(data, redis)

            if user in notified_users:
                break

            await send_notification(user, message)
            await add_notified_user(user, data, redis)
            await asyncio.sleep(.05)
