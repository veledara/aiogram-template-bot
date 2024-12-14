from aiogram.utils.keyboard import InlineKeyboardBuilder

from settings import settings


def get_user_agreement_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Пользовательское соглашение",
        url=settings.user_agreement_url.get_secret_value(),
    )
    builder.button(text="Я принимаю", callback_data="accept_agreement")
    return builder.as_markup()
