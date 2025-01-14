from aiogram.fsm.state import State, StatesGroup


class AdminMenuSG(StatesGroup):
    MAIN = State()
    ADD_ADMIN = State()
    BAN_USER = State()
    BROADCAST = State()
