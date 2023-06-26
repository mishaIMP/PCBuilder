from aiogram.dispatcher.filters.state import State, StatesGroup


class Main(StatesGroup):
    choose_mode = State()
    get_price_to_find = State()
    add_assembly = State()


class AddState(StatesGroup):
    add_comp = State()
    add_additional = State()
    add_info = State()
    get_name = State()
    get_comp_price = State()
    get_amount = State()
    get_link = State()
