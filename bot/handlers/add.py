from aiogram import types, F, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from ..common.buttons import Buttons
from ..common.dialog import MAIN_MENU_TEXT, AddText
from ..common.helper import display_pc, get_component
from ..common.states import AddState, MainState


async def choose_mode(callback: types.CallbackQuery, state: FSMContext, api):
    markup = Buttons.comp_markup()
    await callback.message.edit_text(AddText.ADD_COMPONENTS, reply_markup=markup)
    await state.update_data()
    res = api.init_pc()
    await state.update_data(info_id=res, comps=[])
    await state.set_state(AddState.add_comp)


async def command_add(message: types.Message, state: FSMContext, api):
    data = await state.get_data()
    await state.update_data(data={})
    if 'info_id' in data:
        api.delete_pc(info_id=data['info_id'])
    res = api.init_pc()
    await state.update_data(info_id=res, comps=[])
    markup = Buttons.comp_markup()
    await message.answer(AddText.ADD_COMPONENTS, reply_markup=markup)
    await state.set_state(AddState.add_comp)


async def add_component(callback: types.CallbackQuery, state: FSMContext, api):
    mode = callback.data
    if mode == 'back':
        await callback.message.edit_text(MAIN_MENU_TEXT, reply_markup=Buttons.start_markup)
        data = await state.get_data()
        await state.update_data(data={})
        api.delete_pc(info_id=data['info_id'])
        await state.set_state(MainState.choose_mode)
    elif mode == 'save':
        data = await state.get_data()
        res = api.get_components(info_id=data['info_id'])
        await callback.message.edit_text(text=display_pc(res), parse_mode='HTML', reply_markup=Buttons.final_markup())
        await state.set_state(AddState.save_pc)
    elif mode in ('title', 'edit_title'):
        await callback.message.edit_text(AddText.ENTER_TITLE, reply_markup=Buttons.back_markup)
        await state.set_state(AddState.get_title)
    elif mode.startswith('edit_'):
        data = await state.get_data()
        res = api.get_components(info_id=data['info_id'], comp=mode[5:])
        component = get_component(res)
        text = f'модель: {component["model"]}\nцена: {component["price"]}\nколичество: {component["amount"]}\n'
        text += f"ссылка: {component['link']}\n" if component['link'] else ''
        await callback.message.edit_text(text + AddText.EDIT, reply_markup=Buttons.add_info_markup(component))
        await state.update_data(comp=mode[5:], model=component['model'], price=component['price'],
                                amount=component['amount'], link=component['link'])
        await state.set_state(AddState.add_info)
    else:
        await state.update_data(comp=mode)
        await callback.message.edit_text(AddText.ENTER_MODEL)
        await state.set_state(AddState.get_model)


async def get_model(message: types.Message, state: FSMContext):
    model = message.text
    await state.update_data(model=model)
    await message.answer(AddText.ENTER_PRICE)
    await state.set_state(AddState.get_price)


async def get_price(message: types.Message, state: FSMContext):
    price = message.text
    await state.update_data(price=price)
    await message.answer(AddText.ENTER_AMOUNT, reply_markup=Buttons.skip_markup)
    await state.set_state(AddState.get_amount)


async def get_amount(message: types.Message, state: FSMContext):
    amount = message.text
    await state.update_data(amount=amount)
    await message.answer(AddText.ENTER_LINK, reply_markup=Buttons.skip_markup)
    await state.set_state(AddState.get_link)


async def get_link(message: types.Message, state: FSMContext, api):
    link = message.text
    data = await state.get_data()
    amount = data.get('amount', 1)
    api.add_component(comp=data['comp'], model=data['model'], price=data['price'], amount=amount, link=link,
                      info_id=data['info_id'])
    data['comps'].append(data['comp'])
    await state.update_data(data={})
    data_ = {}
    for item in data:
        if item in ('info_id', 'comps', 'assembly_list'):
            data_[item] = data[item]
    await state.update_data(data_)
    await message.answer(AddText.EDIT_BUILD, reply_markup=Buttons.comp_markup(added=data['comps']))
    await state.set_state(AddState.add_comp)


async def skip_amount(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(AddText.ENTER_LINK, reply_markup=Buttons.skip_markup)
    await state.set_state(AddState.get_link)


async def skip_link(callback: types.CallbackQuery, state: FSMContext, api):
    data = await state.get_data()
    api.add_component(comp=data['comp'], model=data['model'], price=data['price'], amount=data.get('amount', 1),
                      info_id=data['info_id'])
    data['comps'].append(data['comp'])
    await state.update_data(data={})
    data_ = {}
    for item in data:
        if item in ('info_id', 'comps', 'assembly_list'):
            data_[item] = data[item]
    await state.update_data(data_)
    await callback.message.edit_text(AddText.EDIT_BUILD, reply_markup=Buttons.comp_markup(added=data['comps']))
    await state.set_state(AddState.add_comp)


async def get_title(message: types.Message, state: FSMContext, api):
    title = message.text
    data = await state.get_data()
    api.add_title(title=title, info_id=data['info_id'])
    comps = data['comps']
    comps.append('title')
    await state.update_data(comps=comps)
    await message.answer(AddText.EDIT, reply_markup=Buttons.comp_markup(added=comps))
    await state.set_state(AddState.add_comp)


async def add_additional(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await callback.message.edit_text(AddText.ENTER_COMPONENT,
                                     reply_markup=Buttons.additional_comp_markup(data['comps']))
    await state.set_state(AddState.add_additional)


async def select_component(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(comp=callback.data)
    await callback.message.edit_text(AddText.ENTER_MODEL)
    await state.set_state(AddState.get_model)


async def back_to_comp_menu(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    comps = data['comps']
    markup = Buttons.comp_markup(added=comps)
    await callback.message.edit_text(AddText.EDIT, reply_markup=markup)
    await state.set_state(AddState.add_comp)


async def add_info(callback: types.CallbackQuery, state: FSMContext, api):
    callback_data = callback.data

    if callback_data == 'model':
        await callback.message.edit_text(AddText.ENTER_MODEL, reply_markup=Buttons.back_markup)
        await state.set_state(AddState.edit_model)
    elif callback_data == 'price':
        await callback.message.edit_text(AddText.ENTER_PRICE, reply_markup=Buttons.back_markup)
        await state.set_state(AddState.edit_price)
    elif callback_data == 'amount':
        await callback.message.edit_text(AddText.ENTER_AMOUNT, reply_markup=Buttons.back_markup)
        await state.set_state(AddState.edit_amount)
    elif callback_data == 'link':
        await callback.message.edit_text(AddText.ENTER_LINK, reply_markup=Buttons.back_markup)
        await state.set_state(AddState.edit_link)
    else:
        data = await state.get_data()
        await state.update_data(data={})

        if callback_data == 'delete':
            api.delete_pc(info_id=data['info_id'], comp=data['comp'])
            if 'comps' in data:
                data['comps'].remove(data['comp'])

        elif callback_data == 'save':
            api.edit_component(comp=data['comp'], model=data['model'], price=data['price'],
                               amount=data.get('amount', 1), link=data.get('link', None),
                               info_id=data['info_id'])

        data_ = {}
        for item in data:
            if item in ('info_id', 'comps', 'assembly_list'):
                data_[item] = data[item]
        await state.update_data(data_)
        markup = Buttons.comp_markup(added=data['comps'])
        await callback.message.edit_text(AddText.EDIT_BUILD, reply_markup=markup)
        await state.set_state(AddState.add_comp)


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
    await message.answer(text + AddText.EDIT_BUILD, reply_markup=Buttons.add_info_markup(data))
    await state.set_state(AddState.add_info)


async def back_to_info_menu(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = f'модель: {data["model"]}\nцена: {data["price"]}\nколичество: {data["amount"]}\n'
    text += f'ссылка: {data["link"]}\n' if data['link'] else ''
    await callback.message.edit_text(text + AddText.EDIT, reply_markup=Buttons.add_info_markup(data))
    await state.set_state(AddState.add_info)


async def select_privacy(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if callback.data == 'change':
        markup = Buttons.comp_markup(added=data['comps'])
        await callback.message.edit_text(AddText.EDIT_BUILD, reply_markup=markup)
        await state.set_state(AddState.add_comp)
    elif callback.data == 'skip':
        await callback.message.edit_text(AddText.PC_SAVED, reply_markup=Buttons.back_to_main_menu)
        await state.set_state(AddState.save_pc)
    else:
        await callback.message.edit_text(AddText.ENTER_AUTHOR)
        await state.set_state(AddState.get_author)


async def get_author(message: types.Message, state: FSMContext, api):
    author = message.text
    data = await state.get_data()
    api.patch_info(info_id=data['info_id'], payload={'author': author})
    await message.answer(AddText.PC_SAVED, reply_markup=Buttons.back_to_main_menu)
    await state.set_state(AddState.save_pc)


async def return_to_main_menu(callback: types.CallbackQuery, state: FSMContext, api):
    data = await state.get_data()
    api.calculate_total_price(info_id=data['info_id'])
    await callback.message.edit_text(MAIN_MENU_TEXT, reply_markup=Buttons.start_markup)
    await state.set_state(MainState.choose_mode)
    await state.update_data(data={})


def register_add_handlers(add_router: Dispatcher):
    add_router.message.register(get_model, AddState.get_model, F.content_type == 'text')
    add_router.message.register(get_price, AddState.get_price, F.text.regexp(r'\d+'))
    add_router.message.register(get_amount, AddState.get_amount, F.text.regexp(r'\d+'))
    add_router.message.register(get_link, AddState.get_link, F.content_type == 'text')
    add_router.message.register(get_title, AddState.get_title, F.content_type == 'text')
    add_router.message.register(get_info, AddState.edit_model, F.content_type == 'text')
    add_router.message.register(get_info, AddState.edit_price, F.content_type == 'text')
    add_router.message.register(get_info, AddState.edit_amount, F.content_type == 'text')
    add_router.message.register(get_info, AddState.edit_link, F.content_type == 'text')
    add_router.message.register(get_author, AddState.get_author, F.content_type == 'text')
    add_router.message.register(command_add, Command('add'))

    add_router.callback_query.register(add_component, AddState.add_comp, ~(F.data == 'additional'))
    add_router.callback_query.register(choose_mode, MainState.choose_mode, F.data == 'add')
    add_router.callback_query.register(skip_amount, AddState.get_amount, F.data == 'skip')
    add_router.callback_query.register(skip_link, AddState.get_link, F.data == 'skip')
    add_router.callback_query.register(add_additional, AddState.add_comp, F.data == 'additional')
    add_router.callback_query.register(select_component, AddState.add_additional)
    add_router.callback_query.register(back_to_comp_menu, AddState.get_title, F.data == 'back')
    add_router.callback_query.register(add_info, AddState.add_info)
    add_router.callback_query.register(back_to_info_menu, AddState.edit_model, F.data == 'back')
    add_router.callback_query.register(back_to_info_menu, AddState.edit_price, F.data == 'back')
    add_router.callback_query.register(back_to_info_menu, AddState.edit_amount, F.data == 'back')
    add_router.callback_query.register(back_to_info_menu, AddState.edit_link, F.data == 'back')
    add_router.callback_query.register(return_to_main_menu, AddState.save_pc, F.data == 'main_menu')
    add_router.callback_query.register(select_privacy, AddState.save_pc)
