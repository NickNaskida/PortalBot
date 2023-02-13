# -*- coding: utf-8 -*-

import json
import logging

from aiogram import Dispatcher, executor, types

from src.utils import format_prices
from src.decorators import rate_limit
from src.middleware import ThrottlingMiddleware
from src.redis import add_user, get_user, unsubscribe_user, get_prices
from src.config import redis, bot, storage

# Initialize dispatcher
dp = Dispatcher(bot, storage=storage)

# Messages
about_message = '⛽️ Portal Bot არის Portal.com.ge-ს ფასების ბოტი, რომელიც შეგატყობინებთ საწვავის ფასების ცვლილებას\n\n' \
                'სხვა საწვავის კომპანიების ფასების ნახვა შეგიძლიათ აქ: sawvavi.tk 🇬🇪'

help_message = '🤖💬 შეგიძლიათ გამოიყენოთ ბოტი შემდეგი ბრძანებებით:\n\n' \
               '/current - დღევანდელი ფასების ნახვა\n/subscribe - ფასების შეტყობინებების გამოწერა\n' \
               '/unsubscribe - ფასების შეტყობინებების გაუქმება\n/help - დახმარება'


@dp.message_handler(commands=['start', 'help'])
@rate_limit(2)
async def send_welcome(message: types.Message) -> None:
    logging.info(f'User {message.from_user.id} started bot')

    # Create reply keyboard
    reply_markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    about_butt = types.KeyboardButton('🤖 ბოტის შესახებ')
    manual_butt = types.KeyboardButton('🆘 დახმარება')
    reply_markup.add(about_butt, manual_butt)

    logging.info(f'User {message.from_user.id} started bot')

    # Send welcome message
    await message.answer(about_message)
    await message.answer(help_message, reply_markup=reply_markup)


@dp.message_handler(lambda message: message.text == "🤖 ბოტის შესახებ")
@rate_limit(2, '🤖 ბოტის შესახებ')
async def send_about(message: types.Message) -> None:
    """Send about message"""
    await message.answer(about_message)


@dp.message_handler(lambda message: message.text == "🆘 დახმარება")
@rate_limit(2, '🆘 დახმარება')
async def send_help(message: types.Message) -> None:
    """Send manual message"""
    await message.answer(help_message)


@dp.message_handler(commands=['current'])
@rate_limit(5)
async def current_prices(message: types.Message) -> None:
    """Send current prices."""
    prices = await get_prices(redis)

    if not prices:
        await message.answer('დღევანდელი ფასები ვერ მოიძებნა, სცადეთ მოგვიანებით.')
        return

    prices = json.loads(prices)
    formatted_prices = format_prices(prices)

    await message.answer(f'🤖💬 მიმდინარე ფასები:\n\n{formatted_prices}', parse_mode='Markdown')


@dp.message_handler(commands=['subscribe'])
@rate_limit(5)
async def subscribe(message: types.Message) -> None:
    """Subscribe to price notifications."""
    try:
        user = await get_user(message.from_user.id, redis)

        if user:
            await message.answer('თქვენ უკვე გამოწერილი გაქვთ ფასების შეტყობინებები')
            return
        else:
            await add_user(message.from_user.id, redis)
            await message.answer('თქვენ გამოიწერეთ ფასების შეტყობინებები')
    except Exception as e:
        logging.error(f"Error while subscribing user {message.from_user.id}: {e}")
        await message.answer('შეცდომა გამოწერის დროს, გთხოვთ გაიმეოროთ მოთხოვნა')


@dp.message_handler(commands=['unsubscribe'])
@rate_limit(5)
async def unsubscribe(message: types.Message) -> None:
    """Unsubscribe from price notifications."""

    try:
        user = await get_user(message.from_user.id, redis)

        if user:
            await unsubscribe_user(message.from_user.id, redis)
            await message.answer('თქვენ გააუქმეთ ფასების შეტყობინებები.')
        else:
            await message.answer('თქვენ უკვე გაუქმებული გაქვთ ფასების შეტყობინებები')
            return
    except Exception as e:
        logging.error(f"Error while subscribing user {message.from_user.id}: {e}")
        await message.answer('შეცდომა გამოწერის გაუქმების დროს, გთხოვთ გაიმეოროთ მოთხოვნა')


if __name__ == '__main__':
    dp.middleware.setup(ThrottlingMiddleware())
    executor.start_polling(dp, skip_updates=True)
