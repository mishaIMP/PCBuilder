from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from dotenv import load_dotenv
import os

from .helper import show_pc
from .states import AddState, Main
from .buttons import start_markup, build_comp_markup, add_info_markup, back_markup, skip_markup
from .validators import validate_price_range
from .api import Api

load_dotenv()
TOKEN = os.getenv('TOKEN')
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)
api = Api(os.getenv('IP'))


@dp.message_handler(commands='start')
async def start(message: types.Message, state: FSMContext):
    text = '/find - Найти сборку 🔍\n/add - Добавить сборку ➕\n/my - мои сборки 🖥'
    await bot.send_message(message.chat.id, text, reply_markup=start_markup)
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
        if not api.delete_pc(data['info_id']):
            await message.answer('произошла ошибка ')
    res = api.init_pc(data['user_id'])
    if res:
        await state.update_data(comp_id=res['info_id'])
    else:
        await message.answer('произошла ошибка')
    await state.update_data(count_additional=0, user_id=data['user_id'])
    markup = build_comp_markup([])
    await message.answer('добавь комплектующие', reply_markup=markup)
    await AddState.add_comp.set()


@dp.message_handler(commands='find', state='*')
async def command_find(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.reset_data()
    if 'info_id' in data:
        if not api.delete_pc(data['info_id']):
            await message.answer('произошла ошибка')
    await state.update_data(user_id=data['user_id'])
    await message.answer('Введи диапазон цены в формате:\nмин_цена-макс_цена')
    await Main.get_price_to_find.set()


@dp.message_handler(commands='my', state='*')
async def command_my(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.reset_data()
    if 'info_id' in data:
        if not api.delete_pc(data['info_id']):
            await message.answer('произошла ошибка')
    await state.update_data(user_id=data['user_id'])


@dp.message_handler(state=Main.get_price_to_find)
async def get_min_price(message: types.Message, state: FSMContext):
    prices = message.text.strip()
    if validate_price_range(prices):
        await state.update_data(min_price=prices.split('-')[0])
        await state.update_data(max_price=prices.split('-')[1])
        await message.answer('a')
    else:
        await message.answer('цены введены неправильно')
        await Main.get_price_to_find.set()


@dp.callback_query_handler(state=Main.choose_mode)
async def choose_mode(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == 'add':
        markup = build_comp_markup([])
        await callback.message.edit_text('добавить комплектующие', reply_markup=markup)
        await state.update_data(count_additional=0)
        data = await state.get_data()
        res = api.init_pc(data['user_id'])
        if res:
            await state.update_data(comp_id=res['info_id'], user_id=data['user_id'])
        await AddState.add_comp.set()
    elif callback.data == 'find':
        await callback.message.edit_text('Введи диапазон цены в формате:\nмин_цена-макс_цена', reply_markup=back_markup)
        await Main.get_price_to_find.set()
    else:
        pass


@dp.callback_query_handler(state=Main.get_price_to_find)
async def back_to_start_menu(callback: types.CallbackQuery):
    text = '/find - Найти сборку 🔍\n/add - Добавить сборку ➕'
    await callback.message.edit_text(text, reply_markup=start_markup)
    await Main.choose_mode.set()


@dp.callback_query_handler(lambda c: c.data != 'additional', state=AddState.add_comp)
async def add_comp(callback: types.CallbackQuery, state: FSMContext):
    mode = callback.data
    if mode == 'back':
        text = '/find - Найти сборку 🔍\n/add - Добавить сборку ➕'
        await callback.message.edit_text(text, reply_markup=start_markup)
        data = await state.get_data()
        await state.reset_data()
        await state.update_data(user_id=data['user_id'])
        if not api.delete_pc(data['info_id']):
            await callback.answer('произошла ошибка')
        await Main.choose_mode.set()
    elif mode == 'save':
        await callback.message.edit_text('сборка сохранена')
        data = await state.get_data()
        res = api.get_pc(data['info_id'])
        if not res:
            await callback.answer('произошла ошибка')
        else:
            text = show_pc(res)
            await callback.message.answer(text=text, parse_mode='html')
    elif mode in ('title', 'edit_title'):
        await callback.message.edit_text('введи название сборки', reply_markup=back_markup)
        await AddState.get_title.set()
    elif mode.startswith('edit_'):
        data = await state.get_data()
        info = api.get_pc(comp_id=data['info_id'], comp=mode[5:])
        await callback.message.edit_text('изменить', reply_markup=add_info_markup(info))
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
    await message.answer('введи количество (1 по умолчанию)', reply_markup=skip_markup)
    await AddState.get_amount.set()


@dp.message_handler(state=AddState.get_amount)
async def get_amount(message: types.Message, state: FSMContext):
    amount = message.text
    await state.update_data(amount=amount)
    await message.answer('введи ссылку', reply_markup=skip_markup)
    await AddState.get_link.set()


@dp.message_handler(state=AddState.get_link)
async def get_link(message: types.Message, state: FSMContext):
    link = message.text
    data = await state.get_data()
    amount = data.get('amount', 1)
    res = api.add_comp(comp=data['comp'], model=data['model'], price=data['price'], comp_id=data['info_id'],
                       amount=amount, link=link)
    if not res:
        await message.answer('произошла ошибка')
    comps = data.get('comps', [])
    comps.append(data['comp'])
    count = data.get('count_additional', 0)
    await state.reset_data()
    await state.update_data(comps=comps, count_additional=count, user_id=data['user_id'], comp_id=data['info_id'])
    markup = build_comp_markup(added=comps, count=count)
    await message.answer('изменить сборку', reply_markup=markup)
    await AddState.add_comp.set()


@dp.callback_query_handler(state=AddState.get_amount, text='skip')
async def skip_amount(callback: types.CallbackQuery):
    await callback.message.edit_text('введи ссылку', reply_markup=skip_markup)
    await AddState.get_link.set()


@dp.callback_query_handler(state=AddState.get_link, text='skip')
async def skip_link(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    amount = data.get('amount', 1)
    res = api.add_comp(comp=data['comp'], model=data['model'], price=data['price'], comp_id=data['info_id'],
                       amount=amount)
    if not res:
        await callback.message.answer('произошла ошибка')
    comps = data.get('comps', [])
    comps.append(data['comp'])
    count = data.get('count_additional', 0)
    await state.reset_data()
    await state.update_data(comps=comps, count_additional=count, user_id=data['user_id'], comp_id=data['info_id'])
    markup = build_comp_markup(added=comps, count=count)
    await callback.message.edit_text('изменить сборку', reply_markup=markup)
    await AddState.add_comp.set()


@dp.message_handler(state=AddState.get_title)
async def get_title(message: types.Message, state: FSMContext):
    title = message.text
    data = await state.get_data()
    if not api.add_title(title, comp_id=data['info_id']):
        await message.reply('произошла ошибка')
    comps = data.get('comps', [])
    comps.append('title')
    count = data.get('count_additional', 0)
    await state.update_data(comps=comps)
    markup = build_comp_markup(added=comps, count=count)
    await message.answer('изменить', reply_markup=markup)
    await AddState.add_comp.set()


@dp.callback_query_handler(text='additional', state=AddState.add_comp)
async def add_additional(callback: types.CallbackQuery):
    await callback.message.edit_text('какое комплектующее хочешь добавить?', reply_markup=back_markup)
    await AddState.add_additional.set()


@dp.message_handler(state=AddState.add_additional)
async def get_comp_name(message: types.Message, state: FSMContext):
    comp_name = message.text
    data = await state.get_data()
    data['count_additional'] += 1
    data['comp'] = comp_name
    await state.reset_data()
    await state.update_data(data)
    await message.answer('добавить', reply_markup=add_info_markup([]))
    await AddState.add_info.set()


@dp.callback_query_handler(state=[AddState.add_additional, AddState.get_title], text='back')
async def back_to_comp_menu(callback: types.CallbackQuery, state: FSMContext):
    added = await state.get_data()
    comps = added.get('comps', [])
    count = added.get('count_additional', 0)
    markup = build_comp_markup(added=comps, count=count)
    await callback.message.edit_text('изменить', reply_markup=markup)
    await AddState.add_comp.set()


@dp.callback_query_handler(state=AddState.add_info)
async def add_info(callback: types.CallbackQuery, state: FSMContext):
    callback_data = callback.data

    if callback_data == 'model':
        await callback.message.edit_text('введи название', reply_markup=back_markup)
        await AddState.get_model.set()
    elif callback_data == 'price':
        await callback.message.edit_text('введи цену', reply_markup=back_markup)
        await AddState.get_price.set()
    elif callback_data == 'amount':
        await callback.message.edit_text('введи количество', reply_markup=back_markup)
        await AddState.get_amount.set()
    elif callback_data == 'link':
        await callback.message.edit_text('введи ссылку', reply_markup=back_markup)
        await AddState.get_link.set()
    else:
        added = await state.get_data()
        await state.reset_data()
        if callback_data in ('back', 'delete'):
            count = added['count_additional']
            comps = added.get('comps', [])
            components = ['cpu', 'gpu', 'motherboard', 'ram', 'storage', 'case', 'psu', 'culler', 'fan']
            if added['comp'] not in components:
                if count != 0:
                    count -= 1
            await state.update_data(count_additional=count, comps=comps, user_id=added['user_id'],
                                    comp_id=added['info_id'])
            if callback.data == 'delete':
                if not api.delete_pc(added['info_id'], comp=added['comp']):
                    await callback.answer('произошла ошибка')
            markup = build_comp_markup(added=comps, count=count)
            await callback.message.edit_text('изменить комплектующие', reply_markup=markup)
            await AddState.add_comp.set()
        else:
            added = await state.get_data()
            comps = added.get('comps', [])
            count = added.get('count_additional', 0)
            comp = added['comp']
            model = added['model']
            price = added['price']
            amount = added['amount']
            comp_id = added['info_id']
            link = added.get('link', None)
            if not api.add_comp(comp=comp, model=model, price=price, amount=amount, comp_id=comp_id, link=link):
                await callback.answer('произошла ошибка')
            comps.append(added['comp'])

        await state.update_data(comps=comps, count_additional=count, user_id=added['user_id'], comp_id=added['info_id'])
        markup = build_comp_markup(added=comps, count=count)
        await callback.message.edit_text('изменить сборку', reply_markup=markup)
        await AddState.add_comp.set()


@dp.message_handler(state=[AddState.get_model, AddState.get_price, AddState.get_amount, AddState.get_link])
async def get_info(message: types.Message, state: FSMContext):
    text = message.text
    current_state = await state.get_state()
    if current_state == 'AddState:get_model':
        await state.update_data(model=text)
    elif current_state == 'AddState:get_price':
        await state.update_data(price=text)
    elif current_state == 'AddState:get_amount':
        await state.update_data(amount=text)
    else:
        await state.update_data(link=text)
    data = await state.get_data()
    await message.answer('изменить', reply_markup=add_info_markup(data.keys()))
    await AddState.add_info.set()


@dp.callback_query_handler(state=[AddState.get_model, AddState.get_price, AddState.get_amount, AddState.get_link])
async def back_to_info_menu(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await callback.message.edit_text('добавить', reply_markup=add_info_markup(data.keys()))
    await AddState.add_info.set()


executor.start_polling(dp, skip_updates=True)
