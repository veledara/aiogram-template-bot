from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from settings import settings
import logging

from models.base import Base

logger = logging.getLogger(__name__)

engine = create_async_engine(settings.db_url.get_secret_value(), echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db(engine: AsyncEngine):
    """
    Инициализация базы данных: удаление всех таблиц и их повторное создание.
    """
    async with engine.begin() as conn:
        logger.info("Удаляем все таблицы...")
        await conn.run_sync(Base.metadata.drop_all)

        # Создаём таблицы заново
        logger.info("Создаём таблицы заново...")
        await conn.run_sync(Base.metadata.create_all)

        logger.info("Все таблицы созданы.")
