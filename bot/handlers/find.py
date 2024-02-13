from aiogram import types, F, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.common.buttons import Buttons
from bot.common.dialog import MAIN_MENU_TEXT, ERROR_TEXT, FindText
from bot.common.helper import display_pc
from bot.common.imports import api
from bot.common.states import FindState, MainState


async def choose_mode(callback: types.CallbackQuery, state: FSMContext):
    filters = {'min_price': None, 'max_price': None, 'author': None, 'title': None, 'date': None}
    await state.update_data(filters=filters)
    await callback.message.edit_text(FindText.ADD_FILTERS, reply_markup=Buttons.filter_markup(filters))
    await state.set_state(FindState.choose_filters)


async def command_find(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(data={})
    if 'info_id' in data:
        if not api.delete_pc(info_id=data['info_id']):
            await message.answer(ERROR_TEXT)
    filters = {'min_price': None, 'max_price': None, 'author': None, 'title': None, 'date': None}
    await state.update_data(filters=filters)
    await message.answer(FindText.ADD_FILTERS, reply_markup=Buttons.filter_markup(filters))
    await state.set_state(FindState.choose_filters)


async def choose_filters(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == 'back':
        await callback.message.edit_text(MAIN_MENU_TEXT, reply_markup=Buttons.start_markup())
        await state.update_data(data={})
        await state.set_state(MainState.choose_mode)
    elif callback.data == 'min_price':
        await callback.message.edit_text(FindText.ENTER_MIN_PRICE)
        await state.set_state(FindState.get_min_price)
    elif callback.data == 'max_price':
        await callback.message.edit_text(FindText.ENTER_MAX_PRICE)
        await state.set_state(FindState.get_max_price)
    elif callback.data == 'author':
        await callback.message.edit_text(FindText.ENTER_USERNAME)
        await state.set_state(FindState.get_author)
    elif callback.data == 'title':
        await callback.message.edit_text(FindText.ENTER_TITLE)
        await state.set_state(FindState.get_title)
    elif callback.data == 'date':
        await callback.message.edit_text(FindText.SELECT_TIME_PERIOD, reply_markup=Buttons.time_markup())
        await state.set_state(FindState.get_date)
    elif callback.data == 'no filters':
        data = await state.get_data()
        data['filters']['min_price'] = None
        data['filters']['max_price'] = None
        data['filters']['author'] = None
        data['filters']['date'] = None
        data['filters']['title'] = None
        await state.update_data(data)
        await callback.message.edit_text(FindText.ADD_FILTERS, reply_markup=Buttons.filter_markup(data['filters']))
    else:
        await callback.message.edit_text(FindText.SEARCHING)
        data = await state.get_data()
        res = api.get_id_list(data['filters'])
        if not res:
            await callback.message.answer(ERROR_TEXT, reply_markup=Buttons.back_markup())
        elif not res['count']:
            await callback.message.answer(FindText.NOTHING_FOUND, reply_markup=Buttons.back_markup())
        else:
            await state.update_data(assembly_list=res['data'], current=0, max=res['count'])
            pc = api.get_whole_pc(info_id=res['data'][0]['id'])
            if not pc:
                await callback.answer(ERROR_TEXT)
            else:
                await callback.message.edit_text(display_pc(pc), parse_mode='MarkdownV2',
                                                 reply_markup=Buttons.show_pc_markup())
                await state.update_data(likes=pc['info']['likes'])

        await state.set_state(FindState.show_pc)


async def show_pc(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if callback.data == 'back':
        await state.update_data(data={})
        await callback.message.edit_text(FindText.ADD_FILTERS, reply_markup=Buttons.filter_markup(data['filters']))
        await state.update_data(filters=data['filters'])
        await state.set_state(FindState.choose_filters)
    else:
        if callback.data == 'prev':
            data['current'] = (data['current'] - 1) % data['max']
            await state.update_data(data)
        elif callback.data == 'next':
            data['current'] = (data['current'] + 1) % data['max']
            await state.update_data(data)
        info_id = data['assembly_list'][data['current']]['id']
        if callback.data == 'like':
            likes = data['likes'] + 1
            if not api.like(info_id=info_id, likes=likes):
                await callback.answer(ERROR_TEXT)

        pc = api.get_whole_pc(info_id=info_id)
        if not pc:
            await callback.answer(ERROR_TEXT)
        else:
            await callback.message.edit_text(display_pc(pc), parse_mode='MarkdownV2',
                                             reply_markup=Buttons.show_pc_markup())
            await state.update_data(likes=pc['info']['likes'])


async def get_min_and_max_price(message: types.Message, state: FSMContext):
    price = message.text
    data = await state.get_data()
    current_state = await state.get_state()
    if current_state == 'FindState:get_min_price':
        data['filters']['min_price'] = price
    else:
        data['filters']['max_price'] = price
    await state.update_data(data)
    await message.answer(FindText.ADD_FILTERS, reply_markup=Buttons.filter_markup(data['filters']))
    await state.set_state(FindState.choose_filters)


async def get_author(message: types.Message, state: FSMContext):
    author = message.text
    data = await state.get_data()
    data['filters']['author'] = author
    await state.update_data(data)
    await message.answer(FindText.ADD_FILTERS, reply_markup=Buttons.filter_markup(data['filters']))
    await state.set_state(FindState.choose_filters)


async def get_title_to_find(message: types.Message, state: FSMContext):
    title = message.text
    data = await state.get_data()
    data['filters']['title'] = title
    await state.update_data(data)
    await message.answer(FindText.ADD_FILTERS, reply_markup=Buttons.filter_markup(data['filters']))
    await state.set_state(FindState.choose_filters)


async def get_date(callback: types.CallbackQuery, state: FSMContext):
    date = callback.data
    data = await state.get_data()
    data['filters']['date'] = date
    await state.update_data(data)
    await callback.message.edit_text(FindText.ADD_FILTERS, reply_markup=Buttons.filter_markup(data['filters']))
    await state.set_state(FindState.choose_filters)


def register_find_handlers(find_router: Dispatcher):
    find_router.message.register(command_find, Command('find'))
    find_router.message.register(get_min_and_max_price, FindState.get_min_price, F.content_type == 'text')
    find_router.message.register(get_min_and_max_price, FindState.get_max_price, F.content_type == 'text')
    find_router.message.register(get_author, FindState.get_author, F.content_type == 'text')
    find_router.message.register(get_title_to_find, FindState.get_title, F.content_type == 'text')

    find_router.callback_query.register(choose_mode, MainState.choose_mode, F.data == 'find')
    find_router.callback_query.register(choose_filters, FindState.choose_filters)
    find_router.callback_query.register(show_pc, FindState.show_pc)
    find_router.callback_query.register(get_date, FindState.get_date)
