from aiogram.dispatcher.filters.state import State, StatesGroup


class Main(StatesGroup):
    choose_mode = State()
    get_price_to_find = State()
    add_assembly = State()


class AddState(StatesGroup):
    add_comp = State()
    add_additional = State()
    get_model = State()
    edit_model = State()
    get_price = State()
    edit_price = State()
    get_amount = State()
    edit_amount = State()
    get_link = State()
    edit_link = State()
    get_title = State()
    add_info = State()
    final_stage = State()
