#!/home/user/project/venv/bin/pythonX.X
# -*- coding: utf-8 -*-

import logging

from environs import Env
from aiogram import Bot, Dispatcher, executor, types


env = Env()
env.read_env()

# Initialize bot and dispatcher
bot = Bot(token=env.str("TOKEN"))
dp = Dispatcher(bot)

# Messages
about_message = '⛽️ Portal Bot არის Portal.com.ge-ს ფასების ბოტი, რომელიც შეგატყობინებთ ფასების ცვლილებას\n\n' \
                'სხვა საწვავის კომპანიების ფასების ნახვა შეგიძლიათ აქ: sawvavi.tk 🇬🇪'

help_message = '🤖💬'


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
async def send_about(message: types.Message):
    """Send about message"""
    await message.answer(about_message)


@dp.message_handler(lambda message: message.text == "🆘 დახმარება")
async def send_help(message: types.Message):
    """Send manual message"""
    await message.answer(help_message)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
