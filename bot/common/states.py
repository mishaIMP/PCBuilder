from aiogram.fsm.state import StatesGroup, State


class MainState(StatesGroup):
    choose_mode = State()


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
    get_author = State()
    add_info = State()
    save_pc = State()


class FindState(StatesGroup):
    choose_filters = State()
    get_min_price = State()
    get_max_price = State()
    get_author = State()
    get_title = State()
    show_pc = State()


class MyState(StatesGroup):
    choose_assembly = State()
    show_pc = State()
