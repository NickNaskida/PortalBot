# -*- coding: utf-8 -*-

import os
import logging
from pathlib import Path

from environs import Env
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from src.decorators import rate_limit
from src.middleware import ThrottlingMiddleware

BASE_DIR = Path(__file__).resolve().parent.parent

env = Env()
env.read_env(os.path.join(BASE_DIR, '.env'))

storage = RedisStorage2(db=env.int('REDIS_DB'))

# Initialize bot and dispatcher
bot = Bot(token=env.str("TOKEN"))
dp = Dispatcher(bot, storage=storage)

# Messages
about_message = '⛽️ Portal Bot არის Portal.com.ge-ს ფასების ბოტი, რომელიც შეგატყობინებთ საწვავის ფასების ცვლილებას\n\n' \
                'სხვა საწვავის კომპანიების ფასების ნახვა შეგიძლიათ აქ: sawvavi.tk 🇬🇪'

help_message = '🤖💬 შეგიძლიათ გამოიყენოთ ბოტი შემდეგი ბრძანებებით:\n\n' \
               '/current - დღევანდელი ფასების ნახვა\n/help - დახმარება'


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    logging.info(f'User {message.from_user.id} started bot')

    # Create reply keyboard
    reply_markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    about_butt = types.KeyboardButton('🤖 ბოტის შესახებ')
    manual_butt = types.KeyboardButton('🆘 დახმარება')
    reply_markup.add(about_butt, manual_butt)

    # Send welcome message
    await message.answer(about_message, reply_markup=reply_markup)


@dp.message_handler(lambda message: message.text == "🤖 ბოტის შესახებ")
@rate_limit(3, '🤖 ბოტის შესახებ')
async def send_about(message: types.Message):
    """Send about message"""
    await message.answer(about_message)


@dp.message_handler(lambda message: message.text == "🆘 დახმარება")
@rate_limit(3, '🆘 დახმარება')
async def send_help(message: types.Message):
    """Send manual message"""
    await message.answer(help_message)


@dp.message_handler(commands=['current'], )
@rate_limit(5)
async def send_current(message: types.Message):
    """Send current prices"""
    await message.answer('მიმდინარე ფასები')


if __name__ == '__main__':
    dp.middleware.setup(ThrottlingMiddleware())
    executor.start_polling(dp, skip_updates=True)
