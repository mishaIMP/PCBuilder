import aiogram
from aiogram import types
from aiogram.dispatcher import FSMContext

from bot.common.states import MyState, MainState, AddState
from bot.common.imports import api
from bot.common.helper import display_pc, calculate_total_price, get_comps, MAIN_MENU_TEXT, ERROR_TEXT
from bot.common.buttons import Buttons


async def choose_mode(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    res = api.get_title_and_id_list(data['user_id'])
    if not res:
        await callback.message.answer(ERROR_TEXT, reply_markup=Buttons.back_markup())
    elif not res['count']:
        await callback.message.answer('сборок нету(((', reply_markup=Buttons.back_markup())
    else:
        markup = Buttons.my_assemblies(res['data'])
        await callback.message.edit_text('вот твои сборки', reply_markup=markup)
        await state.update_data(assembly_list=res['data'])
    await MyState.choose_assembly.set()


async def command_my(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.reset_data()
    if 'info_id' in data:
        if not api.delete_pc(info_id=data['info_id']):
            await message.answer(ERROR_TEXT)
    res = api.get_title_and_id_list(user_id=data['user_id'])
    if not res:
        await message.answer(ERROR_TEXT, reply_markup=Buttons.back_markup())
    elif not res['count']:
        await message.answer('сборок нету(((', reply_markup=Buttons.back_markup())
    else:
        markup = Buttons.my_assemblies(res['data'])
        await message.answer('вот твои сборки', reply_markup=markup)
        await state.update_data(assembly_list=res['data'])
    await state.update_data(user_id=data['user_id'])
    await MyState.choose_assembly.set()


async def back_to_main_menu(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(MAIN_MENU_TEXT, reply_markup=Buttons.start_markup())
    data = await state.get_data()
    await state.reset_data()
    await state.update_data(user_id=data['user_id'])
    await MainState.choose_mode.set()


async def choose_filters(callback: types.CallbackQuery, state: FSMContext):
    info_id = int(callback.data[9:])
    await state.update_data(info_id=info_id)
    res = api.get_components(info_id=info_id)
    if not res:
        await callback.answer(ERROR_TEXT)
    else:
        await state.update_data(total_price=calculate_total_price(res))
        await callback.message.edit_text(text=display_pc(res), parse_mode='MarkdownV2',
                                         reply_markup=Buttons.build_final_markup(callback.from_user.username, True))
        await MyState.show_pc.set()


async def change_assembly(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if callback.data == 'back':
        markup = Buttons.my_assemblies(data['assembly_list'])
        await callback.message.edit_text('вот твои сборки', reply_markup=markup)
        await MyState.choose_assembly.set()
    elif callback.data == 'change':
        res = api.get_components(info_id=data['info_id'])
        if not res:
            await callback.answer(ERROR_TEXT)
        else:
            comps = get_comps(data=res)
            await state.update_data(comps=comps)
            markup = Buttons.build_comp_markup(added=comps, edit=True)
            await callback.message.edit_text('изменить сборку', reply_markup=markup)
            await AddState.add_comp.set()


def register_all_handlers(dp: aiogram.Dispatcher):
    dp.register_message_handler(command_my, commands='my', state='*')

    dp.register_callback_query_handler(choose_mode, text='my', state=MainState.choose_mode)
    dp.register_callback_query_handler(back_to_main_menu, text='back', state=MyState.choose_assembly)
    dp.register_callback_query_handler(choose_filters, lambda c: c.data.startswith('assembly_'),
                                       state=MyState.choose_assembly)
    dp.register_callback_query_handler(change_assembly, state=MyState.show_pc)
