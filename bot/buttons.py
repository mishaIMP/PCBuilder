from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

find_btn = InlineKeyboardButton('🔍', callback_data='find')
add_btn = InlineKeyboardButton('➕', callback_data='add')
my_btn = InlineKeyboardButton('🖥', callback_data='my')
start_markup = InlineKeyboardMarkup(row_width=2)
start_markup.add(find_btn, add_btn, my_btn)

back_btn = InlineKeyboardButton('🔙', callback_data='back')
back_markup = InlineKeyboardMarkup()
back_markup.add(back_btn)

skip_markup = InlineKeyboardMarkup()
skip_markup.add(InlineKeyboardButton('пропустить', callback_data='skip'))


def add_info_markup(added: dict):
    info = {'модель': 'model', 'цену': 'price', 'количество': 'amount', 'ссылку': 'link'}
    info_markup = InlineKeyboardMarkup(row_width=1)
    is_ready = True
    for key, val in info.items():
        if not val not in ('amount', 'link') and val not in added:
            is_ready = False
        icon = '✏' if added[val] else ''
        btn = InlineKeyboardButton(icon + key + icon, callback_data=val)
        info_markup.add(btn)
    if is_ready:
        save_btn = InlineKeyboardButton('☑', callback_data='save')
        info_markup.add(save_btn, InlineKeyboardButton('🗑', callback_data='delete'))
    else:
        info_markup.add(InlineKeyboardButton('🔙', callback_data='back'))

    return info_markup


def build_comp_markup(added):
    components = {
        'название': 'title',
        'процессор': 'cpu',
        'видеокарту': 'gpu',
        'материнскую плату': 'motherboard',
        'оперативную память': 'ram',
        'HDD/SSD': 'storage',
        'корпус': 'case',
        'блок питания': 'psu',
        'куллер/СЖО': 'culler',
        'корпусные вентиляторы': 'fan'
    }
    comp_markup = InlineKeyboardMarkup(row_width=2)
    is_ready = True
    for key, val in components.items():
        if val not in added:
            is_ready = False
            btn = InlineKeyboardButton(key, callback_data=val)
        else:
            btn = InlineKeyboardButton('✏' + key + '✏', callback_data='edit_' + val)
        comp_markup.add(btn)

    count = 0
    for comp in added:
        if comp not in components.values():
            btn = InlineKeyboardButton('✏' + comp + '✏', callback_data='edit_' + comp)
            comp_markup.add(btn)
            count += 1

    if count < 5:
        comp_markup.add(InlineKeyboardButton('➕', callback_data='additional'))

    if is_ready:
        finish_btn = InlineKeyboardButton('☑', callback_data='save')
        comp_markup.add(finish_btn)

    comp_markup.add(InlineKeyboardButton('удалить сборку', callback_data='back'))

    return comp_markup


def build_final_markup(username):
    markup = InlineKeyboardMarkup()
    change_btn = InlineKeyboardButton('✏', callback_data='change')
    save_anonymously = InlineKeyboardButton('сохранить анонимно', callback_data='save_anonim')
    save_with_username = InlineKeyboardButton(f'сохранить от @{username}', callback_data='save_with_username')
    markup.add(change_btn, save_anonymously, save_with_username)
    return markup
