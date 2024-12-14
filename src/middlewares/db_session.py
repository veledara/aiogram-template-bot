import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Update

from database import async_session

logger = logging.getLogger(__name__)


class DbSessionMiddleware(BaseMiddleware):
    """
    Middleware для предоставления SQLAlchemy сессии в контексте каждого апдейта.
    Сессия автоматически создаётся и передаётся в data,
    после завершения обработки – закрывается.
    """

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        async with async_session() as session:
            data["session"] = session
            try:
                result = await handler(event, data)
                # При необходимости можно здесь коммитить транзакцию
                return result
            except Exception as e:
                logger.error(f"Ошибка во время обработки апдейта: {e}")
                # Ролбэк будет автоматическим, если использовать контекстный менеджер
                # или можно session.rollback() вызвать вручную
                raise
            finally:
                await session.close()
