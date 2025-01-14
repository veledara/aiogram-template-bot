import logging
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest

logger = logging.getLogger(__name__)

async def safe_message_delete(message: Message) -> bool:
    """
    Пытается удалить сообщение.
    Возвращает True, если успешно удалили,
    False, если словили ошибку (например, слишком старое сообщение).
    """
    try:
        await message.delete()
        return True
    except TelegramBadRequest as e:
        logger.warning(f"Не удалось удалить сообщение: {e}")
        return False
    except Exception as e:
        # На всякий случай ловим все ошибки
        logger.warning(f"Ошибка при удалении сообщения: {e}")
        return False
