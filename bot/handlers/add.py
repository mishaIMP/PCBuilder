import aiogram
from aiogram import types
from aiogram.dispatcher import FSMContext

from bot.common.states import AddState, MainState
from bot.common.imports import api
from bot.common.helper import display_pc, calculate_total_price, MAIN_MENU_TEXT, ERROR_TEXT
from bot.common.buttons import Buttons


async def choose_mode(callback: types.CallbackQuery, state: FSMContext):
    markup = Buttons.build_comp_markup([])
    await callback.message.edit_text('добавить комплектующие', reply_markup=markup)
    await state.update_data()
    res = api.init_pc()
    if res:
        await state.update_data(info_id=res, comps=[])
        await AddState.add_comp.set()
    else:
        await callback.answer(ERROR_TEXT)


async def command_add(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.reset_data()
    if 'info_id' in data:
        if not api.delete_pc(info_id=data['info_id']):
            await message.answer(ERROR_TEXT)
    res = api.init_pc()
    if res:
        await state.update_data(info_id=res, comps=[])
        markup = Buttons.build_comp_markup([])
        await message.answer('добавь комплектующие', reply_markup=markup)
        await AddState.add_comp.set()
    else:
        await message.answer(ERROR_TEXT)


async def add_component(callback: types.CallbackQuery, state: FSMContext):
    mode = callback.data
    if mode == 'back':
        await callback.message.edit_text(MAIN_MENU_TEXT, reply_markup=Buttons.start_markup())
        data = await state.get_data()
        await state.reset_data()
        if not api.delete_pc(info_id=data['info_id']):
            await callback.answer(ERROR_TEXT)
        await MainState.choose_mode.set()
    elif mode == 'save':
        data = await state.get_data()
        res = api.get_components(info_id=data['info_id'])
        if not res:
            await callback.answer(ERROR_TEXT)
        else:
            await state.update_data(total_price=calculate_total_price(res))
            await callback.message.answer(text=display_pc(res), parse_mode='MarkdownV2',
                                          reply_markup=Buttons.build_final_markup(callback.from_user.username))
            await AddState.save_pc.set()
    elif mode == 'edit_save':
        pass
    elif mode in ('title', 'edit_title'):
        await callback.message.edit_text('введи название сборки', reply_markup=Buttons.back_markup())
        await AddState.get_title.set()
    elif mode.startswith('edit_'):
        data = await state.get_data()
        res = api.get_components(info_id=data['info_id'], comp=mode[5:])
        if res:
            if res['comps']['count']:
                component = res['comps']['components'][0]
            elif res['additional']['count']:
                component = res['additional']['components'][0]
            else:
                component = {'model': '-', 'price': '-', 'amount': '-', 'link': ''}
            text = f'модель: {component["model"]}\nцена: {component["price"]}\nколичество: {component["amount"]}\n'
            text += f"ссылка: {component['link']}\n" if component['link'] else ''
            await callback.message.edit_text(text + 'изменить', reply_markup=Buttons.add_info_markup(component))
            await state.update_data(comp=mode[5:], model=component['model'], price=component['price'],
                                    amount=component['amount'], link=component['link'])
            await AddState.add_info.set()
        else:
            await callback.answer(ERROR_TEXT)
    else:
        await state.update_data(comp=mode)
        await callback.message.edit_text('введи название модели')
        await AddState.get_model.set()


async def get_model(message: types.Message, state: FSMContext):
    model = message.text
    await state.update_data(model=model)
    await message.answer('введи цену')
    await AddState.get_price.set()


async def get_price(message: types.Message, state: FSMContext):
    price = message.text
    await state.update_data(price=price)
    await message.answer('введи количество (1 по умолчанию)', reply_markup=Buttons.skip_markup())
    await AddState.get_amount.set()


async def get_amount(message: types.Message, state: FSMContext):
    amount = message.text
    await state.update_data(amount=amount)
    await message.answer('введи ссылку', reply_markup=Buttons.skip_markup())
    await AddState.get_link.set()


async def get_link(message: types.Message, state: FSMContext):
    link = message.text
    data = await state.get_data()
    amount = data.get('amount', 1)
    res = api.add_component(comp=data['comp'], model=data['model'], price=data['price'], amount=amount, link=link,
                            info_id=data['info_id'])
    if not res:
        await message.answer(ERROR_TEXT)
    data['comps'].append(data['comp'])
    await state.reset_data()
    data_ = {}
    for item in data:
        if item in ('info_id', 'comps', 'assembly_list'):
            data_[item] = data[item]
    await state.update_data(data_)
    markup = Buttons.build_comp_markup(added=data['comps'])
    await message.answer('изменить сборку', reply_markup=markup)
    await AddState.add_comp.set()


async def skip_amount(callback: types.CallbackQuery):
    await callback.message.edit_text('введи ссылку', reply_markup=Buttons.skip_markup())
    await AddState.get_link.set()


async def skip_link(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    res = api.add_component(comp=data['comp'], model=data['model'], price=data['price'], amount=data.get('amount', 1),
                            info_id=data['info_id'])
    if not res:
        await callback.message.answer(ERROR_TEXT)
    data['comps'].append(data['comp'])
    await state.reset_data()
    data_ = {}
    for item in data:
        if item in ('info_id', 'comps', 'assembly_list'):
            data_[item] = data[item]
    await state.update_data(data_)
    markup = Buttons.build_comp_markup(added=data['comps'])
    await callback.message.edit_text('изменить сборку', reply_markup=markup)
    await AddState.add_comp.set()


async def get_title(message: types.Message, state: FSMContext):
    title = message.text
    data = await state.get_data()
    if not api.add_title(title, info_id=data['info_id']):
        await message.reply(ERROR_TEXT)
    comps = data['comps']
    comps.append('title')
    await state.update_data(comps=comps)
    markup = Buttons.build_comp_markup(added=comps)
    await message.answer('изменить', reply_markup=markup)
    await AddState.add_comp.set()


async def add_additional(callback: types.CallbackQuery):
    await callback.message.edit_text('какое комплектующее хочешь добавить?', reply_markup=Buttons.back_markup())
    await AddState.add_additional.set()


async def get_comp_name(message: types.Message, state: FSMContext):
    comp_name = message.text
    await state.update_data(comp=comp_name)
    await message.answer('введи название модели')
    await AddState.get_model.set()


async def back_to_comp_menu(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    comps = data['comps']
    markup = Buttons.build_comp_markup(added=comps)
    await callback.message.edit_text('изменить', reply_markup=markup)
    await AddState.add_comp.set()


async def add_info(callback: types.CallbackQuery, state: FSMContext):
    callback_data = callback.data

    if callback_data == 'model':
        await callback.message.edit_text('введи название', reply_markup=Buttons.back_markup())
        await AddState.edit_model.set()
    elif callback_data == 'price':
        await callback.message.edit_text('введи цену', reply_markup=Buttons.back_markup())
        await AddState.edit_price.set()
    elif callback_data == 'amount':
        await callback.message.edit_text('введи количество', reply_markup=Buttons.back_markup())
        await AddState.edit_amount.set()
    elif callback_data == 'link':
        await callback.message.edit_text('введи ссылку', reply_markup=Buttons.back_markup())
        await AddState.edit_link.set()
    else:
        data = await state.get_data()
        await state.reset_data()

        if callback_data == 'delete':

            if not api.delete_pc(info_id=data['info_id'], comp=data['comp']):
                await callback.answer(ERROR_TEXT)
            if 'comps' in data:
                data['comps'].remove(data['comp'])

        elif callback_data == 'save':
            if not api.edit_component(comp=data['comp'], model=data['model'], price=data['price'],
                                      amount=data.get('amount', 1), link=data.get('link', None),
                                      info_id=data['info_id']):
                await callback.answer(ERROR_TEXT)
        data_ = {}
        for item in data:
            if item in ('info_id', 'comps', 'assembly_list'):
                data_[item] = data[item]
        await state.update_data(data_)
        markup = Buttons.build_comp_markup(added=data['comps'])
        await callback.message.edit_text('изменить сборку', reply_markup=markup)
        await AddState.add_comp.set()


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
    await message.answer(text + 'изменить', reply_markup=Buttons.add_info_markup(data))
    await AddState.add_info.set()


async def back_to_info_menu(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = f'модель: {data["model"]}\nцена: {data["price"]}\nколичество: {data["amount"]}\n'
    text += f'ссылка: {data["link"]}\n' if data['link'] else ''
    await callback.message.edit_text(text + 'изменить', reply_markup=Buttons.add_info_markup(data))
    await AddState.add_info.set()


async def select_privacy(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if callback.data == 'change':
        markup = Buttons.build_comp_markup(added=data['comps'])
        await callback.message.edit_text('изменить сборку', reply_markup=markup)
        await AddState.add_comp.set()
    else:
        if callback.data == 'save_anonim':
            username = None
        else:
            username = callback.from_user.username
        info = api.get_info(info_id=data['info_id'])
        if not info:
            await callback.answer(ERROR_TEXT)
        else:
            for key in info:
                if key in data:
                    info[key] = data[key]
            info['author'] = username
            if not api.final_save(info_id=data['info_id'], info=info):
                await callback.answer(ERROR_TEXT)
        await callback.message.edit_text('сборка сохранена')
        await callback.message.answer(MAIN_MENU_TEXT, reply_markup=Buttons.start_markup())
        await state.reset_data()
        await MainState.choose_mode.set()


def register_all_handlers(dp: aiogram.Dispatcher):
    dp.register_message_handler(command_add, commands='add', state='*')
    dp.register_message_handler(get_model, content_types='text', state=AddState.get_model)
    dp.register_message_handler(get_price, content_types='text', state=AddState.get_price)
    dp.register_message_handler(get_amount, content_types='text', state=AddState.get_amount)
    dp.register_message_handler(get_link, content_types='text', state=AddState.get_link)
    dp.register_message_handler(get_title, content_types='text', state=AddState.get_title)
    dp.register_message_handler(get_comp_name, content_types='text', state=AddState.add_additional)
    dp.register_message_handler(get_info, content_types='text', state=[AddState.edit_model, AddState.edit_price,
                                                                       AddState.edit_amount, AddState.edit_link])

    dp.register_callback_query_handler(add_component, lambda c: c.data != 'additional', state=AddState.add_comp)
    dp.register_callback_query_handler(choose_mode, text='add', state=MainState.choose_mode)
    dp.register_callback_query_handler(skip_amount, text='skip', state=AddState.get_amount)
    dp.register_callback_query_handler(skip_link, text='skip', state=AddState.get_link)
    dp.register_callback_query_handler(add_additional, text='additional', state=AddState.add_comp)
    dp.register_callback_query_handler(back_to_comp_menu, text='back',
                                       state=[AddState.add_additional, AddState.get_title])
    dp.register_callback_query_handler(add_info, state=AddState.add_info)
    dp.register_callback_query_handler(back_to_info_menu, text='back', state=[AddState.edit_model, AddState.edit_price,
                                                                              AddState.edit_amount, AddState.edit_link])
    dp.register_callback_query_handler(select_privacy, state=AddState.save_pc)
