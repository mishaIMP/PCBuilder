import aiogram
from aiogram import types
from aiogram.dispatcher import FSMContext
from bot.common.states import FindState, MainState
from bot.common.imports import api
from bot.common.helper import display_pc, MAIN_MENU_TEXT, ERROR_TEXT
from bot.common.buttons import Buttons


async def choose_mode(callback: types.CallbackQuery, state: FSMContext):
    filters = {'min_price': None, 'max_price': None, 'author': None, 'title': None, 'date': None}
    await state.update_data(filters=filters)
    await callback.message.edit_text('добавь фильтры', reply_markup=Buttons.filter_markup(filters))
    await FindState.choose_filters.set()


async def command_find(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.reset_data()
    if 'info_id' in data:
        if not api.delete_pc(info_id=data['info_id']):
            await message.answer(ERROR_TEXT)
    filters = {'min_price': None, 'max_price': None, 'author': None, 'title': None, 'date': None}
    await state.update_data(user_id=data['user_id'], filters=filters)
    await message.answer('добавь фильтры', reply_markup=Buttons.filter_markup(filters))
    await FindState.choose_filters.set()


async def choose_filters(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == 'back':
        await callback.message.edit_text(MAIN_MENU_TEXT, reply_markup=Buttons.start_markup())
        data = await state.get_data()
        await state.reset_data()
        await state.update_data(user_id=data['user_id'])
        await MainState.choose_mode.set()
    elif callback.data == 'min_price':
        await callback.message.edit_text('введи минимальную цену')
        await FindState.get_min_price.set()
    elif callback.data == 'max_price':
        await callback.message.edit_text('введи максимальную цену')
        await FindState.get_max_price.set()
    elif callback.data == 'author':
        await callback.message.edit_text('введи username автора')
        await FindState.get_author.set()
    elif callback.data == 'title':
        await callback.message.edit_text('введи название сборки')
        await FindState.get_title.set()
    elif callback.data == 'date':
        await callback.message.edit_text('выбери промежуток времени', reply_markup=Buttons.time_markup())
        await FindState.get_date.set()
    elif callback.data == 'no filters':
        data = await state.get_data()
        data['filters']['min_price'] = None
        data['filters']['max_price'] = None
        data['filters']['author'] = None
        data['filters']['date'] = None
        data['filters']['title'] = None
        await state.update_data(data)
        await callback.message.edit_text('добавь фильтры', reply_markup=Buttons.filter_markup(data['filters']))
    else:
        await callback.message.edit_text('поиск...')
        data = await state.get_data()
        res = api.get_id_list(data['filters'])
        if not res:
            await callback.message.answer(ERROR_TEXT, reply_markup=Buttons.back_markup())
        elif not res['count']:
            await callback.message.answer('ничего не найдено😔😔😔', reply_markup=Buttons.back_markup())
        else:
            await state.update_data(assembly_list=res['data'], current=0, max=res['count'])
            pc = api.get_whole_pc(info_id=res['data'][0]['id'])
            if not pc:
                await callback.answer(ERROR_TEXT)
            else:
                await callback.message.edit_text(display_pc(pc), parse_mode='MarkdownV2',
                                                 reply_markup=Buttons.show_pc_markup())
                await state.update_data(likes=pc['info']['likes'])

        await FindState.show_pc.set()


async def show_pc(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if callback.data == 'back':
        await state.reset_data()
        await callback.message.edit_text('добавь фильтры', reply_markup=Buttons.filter_markup(data['filters']))
        await state.update_data(filters=data['filters'], user_id=data['user_id'])
        await FindState.choose_filters.set()
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
    await message.answer('добавь фильтры', reply_markup=Buttons.filter_markup(data['filters']))
    await FindState.choose_filters.set()


async def get_author(message: types.Message, state: FSMContext):
    author = message.text
    data = await state.get_data()
    data['filters']['author'] = author
    await state.update_data(data)
    await message.answer('добавь фильтры', reply_markup=Buttons.filter_markup(data['filters']))
    await FindState.choose_filters.set()


async def get_title_to_find(message: types.Message, state: FSMContext):
    title = message.text
    data = await state.get_data()
    data['filters']['title'] = title
    await state.update_data(data)
    await message.answer('добавь фильтры', reply_markup=Buttons.filter_markup(data['filters']))
    await FindState.choose_filters.set()


async def get_date(callback: types.CallbackQuery, state: FSMContext):
    date = callback.data
    data = await state.get_data()
    data['filters']['date'] = date
    await state.update_data(data)
    await callback.message.edit_text('добавь фильтры', reply_markup=Buttons.filter_markup(data['filters']))
    await FindState.choose_filters.set()


def register_all_handlers(dp: aiogram.Dispatcher):
    dp.register_message_handler(command_find, commands='find', state='*')
    dp.register_message_handler(get_min_and_max_price, content_types='text',
                                state=[FindState.get_min_price, FindState.get_max_price])
    dp.register_message_handler(get_author, content_types='text', state=FindState.get_author)
    dp.register_message_handler(get_title_to_find, content_types='text', state=FindState.get_title)

    dp.register_callback_query_handler(choose_mode, text='find', state=MainState.choose_mode)
    dp.register_callback_query_handler(choose_filters, state=FindState.choose_filters)
    dp.register_callback_query_handler(show_pc, state=FindState.show_pc)
    dp.register_callback_query_handler(get_date, state=FindState.get_date)
