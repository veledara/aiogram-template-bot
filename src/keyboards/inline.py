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


def get_admin_main_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Добавить админа", callback_data="add_admin")
    builder.button(text="Посмотреть статистику", callback_data="stats")
    builder.button(text="Забанить пользователя", callback_data="ban_user")
    builder.button(text="Сделать рассылку", callback_data="broadcast")
    builder.adjust(1)
    return builder.as_markup()


def get_cancel_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Отмена", callback_data="cancel_admin_action")
    return builder.as_markup()
