from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from dotenv import load_dotenv
import os
from states import AddState, Main
from buttons import start_markup, build_comp_markup, add_info_markup, back_markup
from helper import validate_price_range
from api import Api

load_dotenv()
TOKEN = os.getenv('TOKEN')
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)
api = Api()


@dp.message_handler(commands='start')
async def start(message: types.Message, state: FSMContext):
    text = '/find - Найти сборку 🔍\n/add - Добавить сборку ➕'
    await bot.send_message(message.chat.id, text, reply_markup=start_markup)
    await Main.choose_mode.set()


@dp.message_handler(commands='add', state='*')
async def command_add(message: types.Message, state: FSMContext):
    await state.reset_data()
    await state.update_data(count_additional=0)
    markup = build_comp_markup([])
    await message.answer('добавь комплектующие', reply_markup=markup)
    await AddState.add_comp.set()


@dp.message_handler(commands='find', state='*')
async def command_find(message: types.Message, state: FSMContext):
    await message.answer('Введи диапазон цены в формате:\nмин_цена-макс_цена')
    await state.reset_data()
    await Main.get_price_to_find.set()


@dp.message_handler(state=Main.get_price_to_find)
async def get_min_price(message: types.Message, state: FSMContext):
    prices = message.text.strip()
    if validate_price_range(prices):
        await state.update_data(min_price=prices.split('-')[0])
        await state.update_data(max_price=prices.split('-')[1])
        await message.answer('sosi hui')
    else:
        await message.answer('цены введены неправильно')
        await Main.get_price_to_find.set()


@dp.callback_query_handler(state=Main.choose_mode)
async def button_add(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == 'add':
        markup = build_comp_markup([])
        await callback.message.edit_text('добавить комплектующие', reply_markup=markup)
        await state.update_data(count_additional=0)
        await AddState.add_comp.set()
    else:
        await callback.message.edit_text('Введи диапазон цены в формате:\nмин_цена-макс_цена', reply_markup=back_markup)
        await Main.get_price_to_find.set()


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
        await state.reset_data()
        await Main.choose_mode.set()
    elif mode == 'save':
        data = await state.get_data()
        print(data)
        await callback.message.edit_text(str(data))
    else:
        await state.update_data(comp=mode)
        await callback.message.edit_text('добавить', reply_markup=add_info_markup([]))
        await AddState.add_info.set()


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


@dp.callback_query_handler(state=AddState.add_additional, text='back')
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

    if callback_data == 'name':
        await callback.message.edit_text('введи название', reply_markup=back_markup)
        await AddState.get_name.set()
    elif callback_data == 'price':
        await callback.message.edit_text('введи цену', reply_markup=back_markup)
        await AddState.get_comp_price.set()
    elif callback_data == 'amount':
        await callback.message.edit_text('введи количество', reply_markup=back_markup)
        await AddState.get_amount.set()
    elif callback_data == 'link':
        await callback.message.edit_text('введи ссылку', reply_markup=back_markup)
        await AddState.get_link.set()
    elif callback_data == 'back':
        added = await state.get_data()
        count = added['count_additional']
        comps = added.get('comps', [])
        components = ['cpu', 'gpu', 'motherboard', 'ram', 'storage', 'case', 'psu', 'culler', 'fan']
        if added['comp'] not in components:
            if count != 0:
                count -= 1
        await state.reset_data()
        await state.update_data(count_additional=count, comps=comps)
        markup = build_comp_markup(added=comps, count=count)
        await callback.message.edit_text('изменить комплектующие', reply_markup=markup)
        await AddState.add_comp.set()
    else:
        added = await state.get_data()
        comps = added.get('comps', [])
        if comps:
            del added['comps']
        count = added.get('count_additional', 0)
        del added['count_additional']
        api.add_component(**added)
        comps.append(added['comp'])
        await state.reset_data()
        await state.update_data(comps=comps, count_additional=count)
        markup = build_comp_markup(added=comps, count=count)
        await callback.message.edit_text('изменить сборку', reply_markup=markup)
        await AddState.add_comp.set()


@dp.message_handler(state=[AddState.get_name, AddState.get_comp_price, AddState.get_amount, AddState.get_link])
async def get_info(message: types.Message, state: FSMContext):
    text = message.text
    current_state = await state.get_state()
    if current_state == 'AddState:get_name':
        await state.update_data(name=text)
    elif current_state == 'AddState:get_comp_price':
        await state.update_data(price=text)
    elif current_state == 'AddState:get_amount':
        await state.update_data(amount=text)
    else:
        await state.update_data(link=text)
    data = await state.get_data()
    print(data)
    await message.answer('изменить', reply_markup=add_info_markup(data.keys()))
    await AddState.add_info.set()


@dp.callback_query_handler(state=[AddState.get_name, AddState.get_comp_price, AddState.get_amount, AddState.get_link])
async def back_to_info_menu(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await callback.message.edit_text('добавить', reply_markup=add_info_markup(data.keys()))
    await AddState.add_info.set()


executor.start_polling(dp)  # , skip_updates=True
