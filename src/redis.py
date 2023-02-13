import json
from datetime import date, timedelta


async def get_user(user_id, redis):
    return await redis.get(f"user:{user_id}")


async def get_subscribed_users(redis):
    users = []

    for key in await redis.keys("user:*"):
        user_id = key.decode("utf-8").split(":")[1]
        users.append(user_id)

    return users


async def add_user(user_id, redis):
    await redis.set(f"user:{user_id}", 1)


async def unsubscribe_user(user_id, redis):
    await redis.delete(f"user:{user_id}")


async def get_prices(redis):
    today = date.today()

    return await redis.get(f"prices:{today}")


async def get_yesterday_prices(redis):
    yesterday = date.today() - timedelta(days=1)

    return await redis.get(f"prices:{yesterday}")


async def add_prices(prices, redis):
    today = date.today()

    await redis.set(f"prices:{today}", json.dumps(prices))
    await redis.expire(f"prices:{today}", 60 * 60 * 24 * 5)
