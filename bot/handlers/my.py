from aiogram import types, F, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from ..common.buttons import Buttons
from ..common.dialog import MAIN_MENU_TEXT, MyText
from ..common.helper import display_pc, get_comps
from ..common.states import MyState, MainState, AddState


async def choose_mode(callback: types.CallbackQuery, state: FSMContext, api):
    res = api.get_title_and_id_list()
    if not res['count']:
        await callback.message.edit_text(MyText.NOT_PRESENT, reply_markup=Buttons.back_markup)
    else:
        markup = Buttons.my_builds(res['data'])
        await callback.message.edit_text(MyText.YOUR_BUILDS, reply_markup=markup)
        await state.update_data(assembly_list=res['data'])
    await state.set_state(MyState.choose_assembly)


async def command_my(message: types.Message, state: FSMContext, api):
    data = await state.get_data()
    await state.update_data(data={})
    if 'info_id' in data:
        api.delete_pc(info_id=data['info_id'])
    res = api.get_title_and_id_list()
    if not res['count']:
        await message.answer(MyText.NOT_PRESENT, reply_markup=Buttons.back_markup)
    else:
        markup = Buttons.my_builds(res['data'])
        await message.answer(MyText.YOUR_BUILDS, reply_markup=markup)
        await state.update_data(assembly_list=res['data'])
    await state.set_state(MyState.choose_assembly)


async def back_to_main_menu(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(MAIN_MENU_TEXT, reply_markup=Buttons.start_markup)
    await state.update_data(data={})
    await state.set_state(MainState.choose_mode)


async def choose_filters(callback: types.CallbackQuery, state: FSMContext, api):
    info_id = int(callback.data[9:])
    await state.update_data(info_id=info_id)
    res = api.get_components(info_id=info_id)
    await callback.message.edit_text(text=display_pc(res), parse_mode='HTML', reply_markup=Buttons.my_pc_markup)
    await state.set_state(MyState.show_pc)


async def change_assembly(callback: types.CallbackQuery, state: FSMContext, api):
    data = await state.get_data()
    if callback.data == 'back':
        markup = Buttons.my_builds(data['assembly_list'])
        await callback.message.edit_text(MyText.YOUR_BUILDS, reply_markup=markup)
        await state.set_state(MyState.choose_assembly)
    elif callback.data == 'change':
        res = api.get_components(info_id=data['info_id'])
        comps = get_comps(data=res)
        comps.append('title')
        await state.update_data(comps=comps)
        markup = Buttons.comp_markup(added=comps)
        await callback.message.edit_text(MyText.EDIT_PC, reply_markup=markup)
        await state.set_state(AddState.add_comp)


def register_my_handlers(my_router: Dispatcher):
    my_router.message.register(command_my, Command('my'))

    my_router.callback_query.register(choose_mode, MainState.choose_mode, F.data == 'my')
    my_router.callback_query.register(back_to_main_menu, MyState.choose_assembly, F.data == 'back')
    my_router.callback_query.register(choose_filters, MyState.choose_assembly, F.data.startswith('assembly_'))
    my_router.callback_query.register(change_assembly, MyState.show_pc)
