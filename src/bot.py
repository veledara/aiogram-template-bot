import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from settings import settings
from handlers import start, agreement, admin
from database import init_db, engine
from middlewares.user_check import UserCheckMiddleware
from middlewares.db_session import DbSessionMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    try:
        redis = Redis(
            host=settings.redis_host, port=settings.redis_port, decode_responses=True
        )
        storage = RedisStorage(redis=redis)

        await init_db(engine)

        bot = Bot(token=settings.bot_token.get_secret_value())
        bot_info = await bot.get_me()
        logger.info(f"Бот запущен: @{bot_info.username}")
        dp = Dispatcher(storage=storage)

        dp.update.middleware(DbSessionMiddleware())
        dp.update.middleware(UserCheckMiddleware())

        dp.include_router(start.router)
        dp.include_router(agreement.router)
        dp.include_router(admin.router)

        # Пропускаем все накопленные входящие
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Все накопленные сообщения пропущены, начинаем поллинг.")

        await dp.start_polling(bot)
    except Exception as e:
        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(main())
