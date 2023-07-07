from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

find_btn = InlineKeyboardButton('🔍', callback_data='find')
add_btn = InlineKeyboardButton('➕', callback_data='add')
my_btn = InlineKeyboardButton('🖥', callback_data='my')
start_markup = InlineKeyboardMarkup(row_width=2)
start_markup.add(find_btn, add_btn, my_btn)

back_btn = InlineKeyboardButton('🔙', callback_data='back')
back_markup = InlineKeyboardMarkup(row_width=1)
back_markup.add(back_btn)


def add_info_markup(added):
    info = {'модель': 'model', 'цену': 'price', 'количество': 'amount', 'ссылку': 'link'}
    info_markup = InlineKeyboardMarkup(row_width=1)
    is_ready = True
    for key, val in info.items():
        if val not in added and val != 'link':
            is_ready = False
        icon = '✏' if val in added else ''
        btn = InlineKeyboardButton(icon + key + icon, callback_data=val)
        info_markup.add(btn)
    if is_ready:
        save_btn = InlineKeyboardButton('☑', callback_data='save')
        info_markup.add(save_btn)

    info_markup.add(InlineKeyboardButton('🔙', callback_data='back'))

    return info_markup


def build_comp_markup(added, count: int = 0):
    components = {'название': 'title',
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
        if val not in added and val != 'additional':
            is_ready = False
        icon = '✏' if val in added else ''  # ❌
        btn = InlineKeyboardButton(icon + key + icon, callback_data=val)
        comp_markup.add(btn)

    if count == 0:
        additional_btn = InlineKeyboardButton('дополнительные комплектующие', callback_data='additional')
        comp_markup.add(additional_btn)
    elif count < 5:
        num = ['1️⃣', '2️⃣', '3️⃣', '4️⃣'][count - 1]
        additional_btn = InlineKeyboardButton(f'{num}дополнительные комплектующие{num}', callback_data='additional')
        comp_markup.add(additional_btn)

    if is_ready:
        finish_btn = InlineKeyboardButton('☑', callback_data='save')
        comp_markup.add(finish_btn)

    comp_markup.add(InlineKeyboardButton('удалить сборку', callback_data='back'))

    return comp_markup
