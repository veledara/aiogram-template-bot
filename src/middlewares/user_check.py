import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Update, Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.user import User

logger = logging.getLogger(__name__)


class UserCheckMiddleware(BaseMiddleware):
    ALLOWED_CALLBACKS = {"accept_agreement"}

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        session: AsyncSession = data.get("session")

        # Получаем user_id
        user_id = self._extract_user_id(event)
        if user_id is None:
            # Если не удалось получить user_id, пропускаем
            return await handler(event, data)

        # Разрешаем /start в любом случае
        if (
            isinstance(event, Message)
            and event.text
            and event.text.startswith("/start")
        ):
            return await handler(event, data)

        # Разрешаем "accept_agreement" callback
        if isinstance(event, CallbackQuery) and event.data in self.ALLOWED_CALLBACKS:
            return await handler(event, data)

        # Проверяем пользователя
        user = await self._get_user(session, user_id)

        # Если пользователя не существует
        if user is None:
            await self._send_message(
                event, "Пожалуйста, используйте команду /start для регистрации."
            )
            return

        # Если пользователь забанен
        if user.banned:
            await self._send_message(
                event, "Вы заблокированы и не можете использовать бота."
            )
            return

        # Если пользователь не принял пользовательское соглашение
        if not user.agreement_accepted:
            await self._send_message(
                event,
                "Вы должны принять пользовательское соглашение. Используйте команду /start.",
            )
            return

        # Если пользователь существует, не забанен и принято пользовательское соглашение - пропускаем дальше
        return await handler(event, data)

    def _extract_user_id(self, event: Update) -> int | None:
        if hasattr(event, "from_user") and event.from_user:
            return event.from_user.id
        elif isinstance(event, CallbackQuery) and event.from_user:
            return event.from_user.id
        return None

    async def _get_user(self, session: AsyncSession, user_id: int) -> User | None:
        result = await session.execute(select(User).where(User.telegram_id == user_id))
        return result.scalar_one_or_none()

    async def _send_message(self, event: Update, text: str):
        if isinstance(event, Message):
            await event.answer(text)
        elif isinstance(event, CallbackQuery):
            await event.message.answer(text)
            await event.answer()
