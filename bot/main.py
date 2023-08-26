from aiogram import executor, types
from aiogram.dispatcher import FSMContext

from bot.common.states import MainState
from bot.common.imports import dp, api
from bot.common.helper import MAIN_MENU_TEXT, ERROR_TEXT
from bot.common.buttons import Buttons


def main():
    from handlers import add, find, my

    add.register_all_handlers(dp)
    find.register_all_handlers(dp)
    my.register_all_handlers(dp)

    @dp.message_handler(commands='start')
    async def start(message: types.Message, state: FSMContext):
        if not api.login_or_create_user(message.from_user.username, str(message.from_user.id)):
            await message.answer(ERROR_TEXT)
        else:
            await message.answer(MAIN_MENU_TEXT, reply_markup=Buttons.start_markup())
            await state.reset_data()
        await MainState.choose_mode.set()

    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()
