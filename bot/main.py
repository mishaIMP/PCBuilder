from aiogram import executor, types
from aiogram.dispatcher import FSMContext

from bot.common.states import MainState
from bot.common.imports import dp, api
from bot.common.helper import MAIN_MENU_TEXT
from bot.common.buttons import Buttons


def main():
    from handlers import add, find, my

    add.register_all_handlers(dp)
    find.register_all_handlers(dp)
    my.register_all_handlers(dp)

    @dp.message_handler(commands='start')
    async def start(message: types.Message, state: FSMContext):
        await message.answer(MAIN_MENU_TEXT, reply_markup=Buttons.start_markup())
        data = await state.get_data()
        await state.reset_data()
        if 'user_id' not in data:
            user = api.user_exists(message.from_user.username)
            user_id = 1
            if user:
                user_id = user['id']
            else:
                user = api.add_new_user(message.from_user.username)
                if user:
                    user_id = user['id']
            await state.update_data(user_id=user_id)
        await MainState.choose_mode.set()

    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()
