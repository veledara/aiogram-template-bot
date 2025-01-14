from aiogram.filters import BaseFilter
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from models.user import User, UserRole

logger = logging.getLogger(__name__)


class HasRoleFilter(BaseFilter):
    def __init__(self, roles: list[UserRole]):
        self.roles = roles
        super().__init__()

    async def __call__(self, message: Message, session: AsyncSession, **kwargs) -> bool:
        """
        Получаем session из контекста (DbSessionMiddleware),
        далее делаем SQL-запрос, чтобы найти пользователя.
        """
        if not message.from_user:
            logger.warning("HasRoleFilter: message.from_user is None -> пропускаем")
            return False

        user_id = message.from_user.id

        # Пытаемся достать пользователя из базы
        result = await session.execute(select(User).where(User.telegram_id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            logger.error("HasRoleFilter: Пользователь не найден в БД.")
            return False

        if user.role not in self.roles:
            logger.info(
                f"HasRoleFilter: У пользователя роль {user.role}, нужна {self.roles}"
            )
            return False

        logger.info(f"HasRoleFilter: у пользователя {user_id} есть роль {user.role}")
        return True
