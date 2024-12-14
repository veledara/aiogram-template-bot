import logging
import asyncio
from aiogram import Router, types
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(lambda c: c.data == "accept_agreement")
async def on_accept_agreement(callback: types.CallbackQuery, session: AsyncSession):
    telegram_id = callback.from_user.id
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()

    if user and not user.agreement_accepted:
        user.agreement_accepted = True
        await session.commit()
        await callback.message.answer(
            "Спасибо, что приняли пользовательское соглашение!"
        )
        await asyncio.sleep(1)
        await callback.message.answer(
            "Можете приступать к использованию бота.",
        )
    else:
        await callback.message.answer(
            "Соглашение уже было принято или пользователь не найден."
        )

    await callback.answer()
