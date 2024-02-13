from aiogram import Dispatcher
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.common.buttons import Buttons
from bot.common.dialog import ERROR_TEXT, MAIN_MENU_TEXT
from bot.common.imports import api
from bot.common.states import MainState


async def start(message: Message, state: FSMContext):
    if not api.login_or_create_user(str(message.from_user.id), str(message.from_user.id)):
        await message.answer(ERROR_TEXT)
    else:
        await message.answer(MAIN_MENU_TEXT, reply_markup=Buttons.start_markup())
    await state.set_state(MainState.choose_mode)


def register_start_handler(start_router: Dispatcher):
    start_router.message.register(start, CommandStart())
