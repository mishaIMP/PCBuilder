from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from dotenv import load_dotenv
import os

from helper import show_pc, calculate_total_price
from states import AddState, Main, FindState
from buttons import Buttons
from api import Api

load_dotenv()
TOKEN = os.getenv('TOKEN')
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)
api = Api(os.getenv('IP'))
buttons = Buttons()


@dp.message_handler(commands='start')
async def start(message: types.Message, state: FSMContext):
    text = '/find - Найти сборку 🔍\n/add - Добавить сборку ➕\n/my - мои сборки 🖥'
    await bot.send_message(message.chat.id, text, reply_markup=buttons.start_markup())
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
    await Main.choose_mode.set()


@dp.message_handler(commands='add', state='*')
async def command_add(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.reset_data()
    if 'info_id' in data or 'comp_id' in data:
        if not api.delete_pc(comp_id=data['comp_id'], info_id=data['info_id']):
            await message.answer('произошла ошибка')
    res = api.init_pc(data['user_id'])
    if res:
        await state.update_data(comp_id=res['comp_id'], info_id=res['info_id'])
    else:
        await message.answer('произошла ошибка')
    await state.update_data(user_id=data['user_id'], comps=[])
    markup = buttons.build_comp_markup([])
    await message.answer('добавь комплектующие', reply_markup=markup)
    await AddState.add_comp.set()


@dp.message_handler(commands='find', state='*')
async def command_find(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.reset_data()
    if 'info_id' in data or 'comp_id' in data:
        if not api.delete_pc(comp_id=data['comp_id'], info_id=data['info_id']):
            await message.answer('произошла ошибка')
    filters = {
        'min_price': None,
        'max_price': None,
        'author': None,
        'title': None,
        'date': None
    }
    await state.update_data(user_id=data['user_id'], filters=filters)
    await message.answer('добавь фильтры', reply_markup=buttons.filter_markup(filters))
    await FindState.choose_filters.set()


@dp.message_handler(commands='my', state='*')
async def command_my(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.reset_data()
    if 'info_id' in data or 'comp_id' in data:
        if not api.delete_pc(comp_id=data['comp_id'], info_id=data['info_id']):
            await message.answer('произошла ошибка')
    await state.update_data(user_id=data['user_id'])


@dp.callback_query_handler(state=Main.choose_mode)
async def choose_mode(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == 'add':
        markup = buttons.build_comp_markup([])
        await callback.message.edit_text('добавить комплектующие', reply_markup=markup)
        await state.update_data()
        data = await state.get_data()
        res = api.init_pc(data['user_id'])
        if res:
            await state.update_data(comp_id=res['comp_id'], user_id=data['user_id'], info_id=res['info_id'], comps=[])
            await AddState.add_comp.set()
        else:
            await callback.answer('произошла ошибка')
    elif callback.data == 'find':
        filters = {'min_price': None, 'max_price': None, 'author': None, 'title': None, 'date': None}
        await state.update_data(filters=filters)
        await callback.message.edit_text('добавь фильтры', reply_markup=buttons.filter_markup(filters))
        await FindState.choose_filters.set()
    else:
        pass


@dp.callback_query_handler(lambda c: c.data != 'additional', state=AddState.add_comp)
async def add_comp(callback: types.CallbackQuery, state: FSMContext):
    mode = callback.data
    if mode == 'back':
        text = '/find - Найти сборку 🔍\n/add - Добавить сборку ➕\n/my - мои сборки 🖥'
        await callback.message.edit_text(text, reply_markup=buttons.start_markup())
        data = await state.get_data()
        await state.reset_data()
        await state.update_data(user_id=data['user_id'])
        if not api.delete_pc(comp_id=data['comp_id'], info_id=data['info_id']):
            await callback.answer('произошла ошибка')
        await Main.choose_mode.set()
    elif mode == 'save':
        await callback.message.edit_text('сборка сохранена')
        data = await state.get_data()
        res = api.get_components(data['comp_id'])
        if not res:
            await callback.answer('произошла ошибка')
        else:
            await state.update_data(total_price=calculate_total_price(res))
            await callback.message.answer(text=show_pc(res), parse_mode='html',
                                          reply_markup=buttons.build_final_markup(callback.from_user.username))
            await AddState.final_stage.set()
    elif mode in ('title', 'edit_title'):
        await callback.message.edit_text('введи название сборки', reply_markup=buttons.back_markup())
        await AddState.get_title.set()
    elif mode.startswith('edit_'):
        data = await state.get_data()
        info = api.get_components(comp_id=data['comp_id'], comp=mode[5:])
        if info:
            component = info['additional'][0] if 'additional' in info else info[mode[5:]]
            text = f'модель: {component["model"]}\nцена: {component["price"]}\nколичество: {component["amount"]}\n'
            text += f"ссылка: {component['link']}\n" if component['link'] else ''
            await callback.message.edit_text(text + 'изменить', reply_markup=buttons.add_info_markup(component))
            await state.update_data(comp=mode[5:], model=component['model'], price=component['price'],
                                    amount=component['amount'], link=component['link'])
            await AddState.add_info.set()
        else:
            await callback.answer('произошла ошибка')
    else:
        await state.update_data(comp=mode)
        await callback.message.edit_text('введи название модели')
        await AddState.get_model.set()


@dp.message_handler(state=AddState.get_model)
async def get_model(message: types.Message, state: FSMContext):
    model = message.text
    await state.update_data(model=model)
    await message.answer('введи цену')
    await AddState.get_price.set()


@dp.message_handler(state=AddState.get_price)
async def get_price(message: types.Message, state: FSMContext):
    price = message.text
    await state.update_data(price=price)
    await message.answer('введи количество (1 по умолчанию)', reply_markup=buttons.skip_markup())
    await AddState.get_amount.set()


@dp.message_handler(state=AddState.get_amount)
async def get_amount(message: types.Message, state: FSMContext):
    amount = message.text
    await state.update_data(amount=amount)
    await message.answer('введи ссылку', reply_markup=buttons.skip_markup())
    await AddState.get_link.set()


@dp.message_handler(state=AddState.get_link)
async def get_link(message: types.Message, state: FSMContext):
    link = message.text
    data = await state.get_data()
    amount = data.get('amount', 1)
    res = api.add_comp(comp=data['comp'], model=data['model'], price=data['price'], comp_id=data['comp_id'],
                       amount=amount, link=link)
    if not res:
        await message.answer('произошла ошибка')
    data['comps'].append(data['comp'])
    await state.reset_data()
    data = dict(
        map(lambda k: (k, data[k]),
            filter(lambda k: k in ('user_id', 'info_id', 'comp_id', 'comps'), data)))
    await state.update_data(data)
    markup = buttons.build_comp_markup(added=data['comps'])
    await message.answer('изменить сборку', reply_markup=markup)
    await AddState.add_comp.set()


@dp.callback_query_handler(state=AddState.get_amount, text='skip')
async def skip_amount(callback: types.CallbackQuery):
    await callback.message.edit_text('введи ссылку', reply_markup=buttons.skip_markup())
    await AddState.get_link.set()


@dp.callback_query_handler(state=AddState.get_link, text='skip')
async def skip_link(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    res = api.add_comp(comp=data['comp'], model=data['model'], price=data['price'], comp_id=data['comp_id'],
                       amount=data.get('amount', 1))
    if not res:
        await callback.message.answer('произошла ошибка')
    data['comps'].append(data['comp'])
    await state.reset_data()
    data = dict(
        map(lambda k: (k, data[k]),
            filter(lambda k: k in ('user_id', 'info_id', 'comp_id', 'comps'), data)))
    await state.update_data(data)
    markup = buttons.build_comp_markup(added=data['comps'])
    await callback.message.edit_text('изменить сборку', reply_markup=markup)
    await AddState.add_comp.set()


@dp.message_handler(state=AddState.get_title)
async def get_title(message: types.Message, state: FSMContext):
    title = message.text
    data = await state.get_data()
    if not api.add_title(title, info_id=data['info_id']):
        await message.reply('произошла ошибка')
    comps = data['comps']
    comps.append('title')
    await state.update_data(comps=comps)
    markup = buttons.build_comp_markup(added=comps)
    await message.answer('изменить', reply_markup=markup)
    await AddState.add_comp.set()


@dp.callback_query_handler(text='additional', state=AddState.add_comp)
async def add_additional(callback: types.CallbackQuery):
    await callback.message.edit_text('какое комплектующее хочешь добавить?', reply_markup=buttons.back_markup())
    await AddState.add_additional.set()


@dp.message_handler(state=AddState.add_additional)
async def get_comp_name(message: types.Message, state: FSMContext):
    comp_name = message.text
    await state.update_data(comp=comp_name)
    await message.answer('введи название модели')
    await AddState.get_model.set()


@dp.callback_query_handler(state=[AddState.add_additional, AddState.get_title], text='back')
async def back_to_comp_menu(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    comps = data['comps']
    markup = buttons.build_comp_markup(added=comps)
    await callback.message.edit_text('изменить', reply_markup=markup)
    await AddState.add_comp.set()


@dp.callback_query_handler(state=AddState.add_info)
async def add_info(callback: types.CallbackQuery, state: FSMContext):
    callback_data = callback.data

    if callback_data == 'model':
        await callback.message.edit_text('введи название', reply_markup=buttons.back_markup())
        await AddState.edit_model.set()
    elif callback_data == 'price':
        await callback.message.edit_text('введи цену', reply_markup=buttons.back_markup())
        await AddState.edit_price.set()
    elif callback_data == 'amount':
        await callback.message.edit_text('введи количество', reply_markup=buttons.back_markup())
        await AddState.edit_amount.set()
    elif callback_data == 'link':
        await callback.message.edit_text('введи ссылку', reply_markup=buttons.back_markup())
        await AddState.edit_link.set()
    else:
        data = await state.get_data()
        await state.reset_data()

        if callback_data == 'delete':

            if not api.delete_pc(comp_id=data['comp_id'], comp=data['comp']):
                await callback.answer('произошла ошибка')
            if 'comps' in data:
                data['comps'].remove(data['comp'])

        elif callback_data == 'save':
            if not api.add_comp(comp=data['comp'], model=data['model'], price=data['price'],
                                amount=data.get('amount', 1), comp_id=data['comp_id'], link=data.get('link', None)):
                await callback.answer('произошла ошибка')

        await state.update_data(dict(
            map(lambda k: (k, data[k]),
                filter(lambda k: k in ('user_id', 'info_id', 'comp_id', 'comps'), data))))
        markup = buttons.build_comp_markup(added=data['comps'])
        await callback.message.edit_text('изменить сборку', reply_markup=markup)
        await AddState.add_comp.set()


@dp.message_handler(state=[AddState.edit_model, AddState.edit_price, AddState.edit_amount, AddState.edit_link])
async def get_info(message: types.Message, state: FSMContext):
    text = message.text
    current_state = await state.get_state()
    if current_state == 'AddState:edit_model':
        await state.update_data(model=text)
    elif current_state == 'AddState:edit_price':
        await state.update_data(price=text)
    elif current_state == 'AddState:edit_amount':
        await state.update_data(amount=text)
    else:
        await state.update_data(link=text)
    data = await state.get_data()
    text = f'модель: {data["model"]}\nцена: {data["price"]}\nколичество: {data["amount"]}\n'
    text += f"ссылка: {data['link']}\n" if data['link'] else ''
    await message.answer(text + 'изменить', reply_markup=buttons.add_info_markup(data))
    await AddState.add_info.set()


@dp.callback_query_handler(state=[AddState.edit_model, AddState.edit_price, AddState.edit_amount, AddState.edit_link])
async def back_to_info_menu(callback: types.CallbackQuery, state: FSMContext):
    # callback.data == 'back':
    data = await state.get_data()
    text = f'модель: {data["model"]}\nцена: {data["price"]}\nколичество: {data["amount"]}\n'
    text += f'ссылка: {data["link"]}\n' if data['link'] else ''
    await callback.message.edit_text(text + 'изменить', reply_markup=buttons.add_info_markup(data))
    await AddState.add_info.set()


@dp.callback_query_handler(state=AddState.final_stage)
async def final_choice(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if callback.data == 'change':
        markup = buttons.build_comp_markup(added=data['comps'])
        await callback.message.edit_text('изменить сборку', reply_markup=markup)
        await AddState.add_comp.set()
    else:
        if callback.data == 'save_anonim':
            username = None
        else:
            username = callback.from_user.username

        if not api.final_save(info_id=data['info_id'], total_price=data['total_price'], author=username):
            await callback.answer('произошла ошибка')
        await callback.message.edit_text('сборка сохранена')
        text = '/find - Найти сборку 🔍\n/add - Добавить сборку ➕\n/my - мои сборки 🖥'
        await callback.message.answer(text, reply_markup=buttons.start_markup())
        data = await state.get_data()
        await state.reset_data()
        await state.reset_state()
        await state.update_data(user_id=data['user_id'])


@dp.callback_query_handler(state=FindState.choose_filters)
async def choose_filters(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == 'back':
        text = '/find - Найти сборку 🔍\n/add - Добавить сборку ➕\n/my - мои сборки 🖥'
        await callback.message.edit_text(text, reply_markup=buttons.start_markup())
        await Main.choose_mode.set()
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
        await callback.message.edit_text('выбери промежуток времени', reply_markup=buttons.time_markup())
        await FindState.get_date.set()
    elif callback.data == 'no filters':
        data = await state.get_data()
        data['filters']['min_price'] = None
        data['filters']['max_price'] = None
        data['filters']['author'] = None
        data['filters']['date'] = None
        data['filters']['title'] = None
        await state.update_data(data)
        await callback.message.edit_text('добавь фильтры', reply_markup=buttons.filter_markup(data['filters']))
    else:
        await callback.message.edit_text('поиск...')
        data = await state.get_data()
        res = api.get_pc_list(data['filters'])
        if not res:
            await callback.message.edit_text('ничего не найдено😔😔😔', reply_markup=buttons.back_markup())
        else:
            pass


@dp.message_handler(state=[FindState.get_min_price, FindState.get_max_price])
async def get_min_and_max_price(message: types.Message, state: FSMContext):
    price = message.text
    data = await state.get_data()
    current_state = await state.get_state()
    if current_state == 'FindState:get_min_price':
        data['filters']['min_price'] = price
    else:
        data['filters']['max_price'] = price
    await state.update_data(data)
    await message.answer('добавь фильтры', reply_markup=buttons.filter_markup(data['filters']))
    await FindState.choose_filters.set()


@dp.message_handler(state=FindState.get_author)
async def get_author(message: types.Message, state: FSMContext):
    author = message.text
    data = await state.get_data()
    data['filters']['author'] = author
    await state.update_data(data)
    await message.answer('добавь фильтры', reply_markup=buttons.filter_markup(data['filters']))
    await FindState.choose_filters.set()


@dp.message_handler(state=FindState.get_author)
async def get_title_to_find(message: types.Message, state: FSMContext):
    title = message.text
    data = await state.get_data()
    data['filters']['title'] = title
    await state.update_data(data)
    await message.answer('добавь фильтры', reply_markup=buttons.filter_markup(data['filters']))
    await FindState.choose_filters.set()


@dp.callback_query_handler(state=FindState.get_date)
async def get_date(callback: types.CallbackQuery, state: FSMContext):
    date = callback.data
    data = await state.get_data()
    data['filters']['date'] = date
    await state.update_data(data)
    await callback.message.edit_text('добавь фильтры', reply_markup=buttons.filter_markup(data['filters']))
    await FindState.choose_filters.set()


executor.start_polling(dp, skip_updates=True)
