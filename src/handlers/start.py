import logging
from aiogram import Router, types
from aiogram.filters import CommandStart, CommandObject
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.user import User
from keyboards.inline import get_user_agreement_keyboard

logger = logging.getLogger(__name__)

router = Router()


@router.message(CommandStart())
async def cmd_start(
    message: types.Message, command: CommandObject, session: AsyncSession
):
    telegram_id = message.from_user.id
    username = message.from_user.username

    # Извлекаем параметр из команды /start
    referral_code = command.args

    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            telegram_id=telegram_id,
            username=username,
            agreement_accepted=False,
            referral_code=referral_code,
        )
        session.add(user)
        await session.commit()

        await message.answer(
            "Для использования бота необходимо принять пользовательское соглашение.",
            reply_markup=get_user_agreement_keyboard(),
        )
    else:
        if not user.agreement_accepted:
            await message.answer(
                "Для использования бота необходимо принять пользовательское соглашение.",
                reply_markup=get_user_agreement_keyboard(),
            )
        else:
            await message.answer("Привет! Добро пожаловать обратно!")
