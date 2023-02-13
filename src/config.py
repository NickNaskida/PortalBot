import os
from pathlib import Path

import aioredis
from environs import Env
from aiogram import Bot
from aiogram.contrib.fsm_storage.redis import RedisStorage2

BASE_DIR = Path(__file__).resolve().parent.parent

env = Env()
env.read_env(os.path.join(BASE_DIR, '.env'))

BOT_TOKEN = env.str("TOKEN")
REDIS_DB = env.int('REDIS_DB')

bot = Bot(token=BOT_TOKEN)

storage = RedisStorage2(db=REDIS_DB)
redis = aioredis.from_url("redis://localhost/" + str(REDIS_DB))
