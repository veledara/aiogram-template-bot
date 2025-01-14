import logging
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from models.user import User, UserRole
from filters.has_role import HasRoleFilter
from keyboards.inline import get_admin_main_keyboard
from keyboards.inline import get_cancel_keyboard
from states.admin_states import AdminMenuSG
from utils.misc import safe_message_delete

logger = logging.getLogger(__name__)
router = Router()


# -----------------------------
# 1. /admin – вход в админ-меню
# -----------------------------
@router.message(
    Command("admin"), HasRoleFilter(roles=[UserRole.ADMIN]), StateFilter("*")
)
async def admin_menu(message: types.Message, state: FSMContext):
    """
    Показывает главное меню админа (кнопки).
    Переводим админа в состояние MAIN.
    """
    await state.set_state(AdminMenuSG.MAIN)
    await message.answer(
        "Добро пожаловать в админское меню!", reply_markup=get_admin_main_keyboard()
    )


# --------------------------------
# 2. Обработка колбэков из клавиатуры
# --------------------------------
@router.callback_query(
    lambda c: c.data == "add_admin",
    HasRoleFilter(roles=[UserRole.ADMIN]),
    StateFilter(AdminMenuSG.MAIN),
)
async def on_add_admin_callback(callback: types.CallbackQuery, state: FSMContext):
    """
    Кнопка "Добавить админа":
    Просим ввести Telegram ID. Добавляем кнопку «Отмена».
    """
    await state.set_state(AdminMenuSG.ADD_ADMIN)
    await callback.message.answer(
        "Введите Telegram ID пользователя, которого хотите сделать админом.\n"
        "Просто отправьте число сообщением в чат.",
        reply_markup=get_cancel_keyboard(),
    )
    await callback.answer()


@router.callback_query(
    lambda c: c.data == "stats",
    HasRoleFilter(roles=[UserRole.ADMIN]),
    StateFilter(AdminMenuSG.MAIN),
)
async def on_stats_callback(callback: types.CallbackQuery, session: AsyncSession):
    """
    Кнопка "Посмотреть статистику".
    """
    admin_count = await session.scalar(
        select(func.count(User.id)).where(User.role == UserRole.ADMIN)
    )
    user_count = await session.scalar(
        select(func.count(User.id)).where(User.role == UserRole.USER)
    )
    banned_count = await session.scalar(
        select(func.count(User.id)).where(User.banned == True)
    )

    msg = (
        "Статистика:\n\n"
        f"👤 Пользователи (USER): {user_count}\n"
        f"🔧 Админы (ADMIN): {admin_count}\n"
        f"🚫 Забанены: {banned_count}"
    )
    await callback.message.answer(msg)
    await callback.answer()


@router.callback_query(
    lambda c: c.data == "ban_user",
    HasRoleFilter(roles=[UserRole.ADMIN]),
    StateFilter(AdminMenuSG.MAIN),
)
async def on_ban_user_callback(callback: types.CallbackQuery, state: FSMContext):
    """
    Кнопка "Забанить пользователя".
    Просим ввести Telegram ID. Добавляем кнопку «Отмена».
    """
    await state.set_state(AdminMenuSG.BAN_USER)
    await callback.message.answer(
        "Введите Telegram ID пользователя, которого хотите забанить.\n"
        "Просто отправьте число сообщением в чат.",
        reply_markup=get_cancel_keyboard(),
    )
    await callback.answer()


@router.callback_query(
    lambda c: c.data == "broadcast",
    HasRoleFilter(roles=[UserRole.ADMIN]),
    StateFilter(AdminMenuSG.MAIN),
)
async def on_broadcast_callback(callback: types.CallbackQuery, state: FSMContext):
    """
    Кнопка "Сделать рассылку".
    Просим переслать любое сообщение (или ввести текст). Добавляем кнопку «Отмена».
    """
    await state.set_state(AdminMenuSG.BROADCAST)
    await callback.message.answer(
        "Перешлите мне сообщение (или введите текст), чтобы я отправил всем пользователям.",
        reply_markup=get_cancel_keyboard(),
    )
    await callback.answer()


# ------------------------------
# КНОПКА "ОТМЕНА" (cancel_admin_action)
# ------------------------------


@router.callback_query(
    lambda c: c.data == "cancel_admin_action",
    HasRoleFilter(roles=[UserRole.ADMIN]),
    StateFilter(AdminMenuSG.ADD_ADMIN, AdminMenuSG.BAN_USER, AdminMenuSG.BROADCAST),
)
async def on_cancel_admin_action(callback: types.CallbackQuery, state: FSMContext):
    """
    Обработка нажатия "Отмена" во время любого из трёх "режимов".
    Удаляем текущее сообщение (если получится),
    возвращаемся в AdminMenuSG.MAIN,
    показываем заново главное меню, если надо.
    """
    deleted = await safe_message_delete(callback.message)
    # Если сообщение успешно удалили, можно просто ответить "Операция отменена"
    # Но если удалить не получилось (старое сообщение), придётся заново показать меню
    if not deleted:
        await callback.message.answer(
            "Операция отменена.",
            reply_markup=get_admin_main_keyboard(),
        )
    else:
        await callback.message.answer("Операция отменена.")

    await state.set_state(AdminMenuSG.MAIN)
    await callback.answer()


# -----------------------------------------------------
# 3. Обработка "следующего шага" для каждого режима
# -----------------------------------------------------


# --- (a) ADD_ADMIN ---
@router.message(
    HasRoleFilter(roles=[UserRole.ADMIN]), StateFilter(AdminMenuSG.ADD_ADMIN)
)
async def handle_add_admin(
    message: types.Message, session: AsyncSession, state: FSMContext
):
    text = message.text.strip()
    try:
        new_admin_id = int(text)
    except ValueError:
        await message.answer(
            "Это не похоже на число. Попробуйте снова или /admin для выхода."
        )
        return

    user_to_admin = await session.scalar(
        select(User).where(User.telegram_id == new_admin_id)
    )
    if not user_to_admin:
        await message.answer("Пользователь с таким telegram_id не найден в БД.")
        return

    user_to_admin.role = UserRole.ADMIN
    await session.commit()
    await message.answer(f"Пользователь {user_to_admin.telegram_id} теперь админ!")

    await state.set_state(AdminMenuSG.MAIN)


# --- (b) BAN_USER ---
@router.message(
    HasRoleFilter(roles=[UserRole.ADMIN]), StateFilter(AdminMenuSG.BAN_USER)
)
async def handle_ban_user(
    message: types.Message, session: AsyncSession, state: FSMContext
):
    text = message.text.strip()
    try:
        ban_user_id = int(text)
    except ValueError:
        await message.answer(
            "Это не похоже на число. Попробуйте снова или /admin для выхода."
        )
        return

    user_to_ban = await session.scalar(
        select(User).where(User.telegram_id == ban_user_id)
    )
    if not user_to_ban:
        await message.answer("Пользователь с таким telegram_id не найден в БД.")
        return

    user_to_ban.banned = True
    await session.commit()
    await message.answer(f"Пользователь {user_to_ban.telegram_id} забанен!")

    await state.set_state(AdminMenuSG.MAIN)


# --- (c) BROADCAST ---
@router.message(
    HasRoleFilter(roles=[UserRole.ADMIN]), StateFilter(AdminMenuSG.BROADCAST)
)
async def handle_broadcast(
    message: types.Message, session: AsyncSession, state: FSMContext
):
    users = await session.scalars(select(User).where(User.banned == False))
    users_list = users.all()

    if message.forward_from or message.forward_from_chat:
        for user in users_list:
            try:
                await message.bot.copy_message(
                    chat_id=user.telegram_id,
                    from_chat_id=message.chat.id,
                    message_id=message.message_id,
                )
            except Exception as e:
                logger.warning(f"Не удалось переслать {user.telegram_id}: {e}")
    else:
        text_to_send = message.text
        for user in users_list:
            try:
                await message.bot.send_message(
                    chat_id=user.telegram_id, text=text_to_send
                )
            except Exception as e:
                logger.warning(f"Не удалось отправить {user.telegram_id}: {e}")

    await message.answer("Рассылка завершена. Проверьте логи на ошибки.")
    await state.set_state(AdminMenuSG.MAIN)
