from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class Buttons:
    @staticmethod
    def start_markup():
        return InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='🔍', callback_data='find'),
                              InlineKeyboardButton(text='➕', callback_data='add'),
                              InlineKeyboardButton(text='🖥', callback_data='my')]]
        )

    @staticmethod
    def back_markup():
        return InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='🔙назад', callback_data='back')]]
        )

    @staticmethod
    def skip_markup():
        return InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='⏭пропустить', callback_data='skip')]]
        )

    @staticmethod
    def filter_markup(filters: dict):
        builder = InlineKeyboardBuilder()
        filters_ = {
            'min_price': '💴min стоимость',
            'max_price': '💵max стоимость',
            'title': '📝название',
            'author': '🤵‍автор',
            'date': '🗓время'
        }
        time = {'day': 'день', 'week': 'неделя', 'month': 'месяц', '3 months': '3 месяца', 'year': 'год'}
        filter_exists = False
        for i in filters_:
            if filters[i]:
                filter_exists = True
            if i == 'date':
                text = f'{filters_[i]}: {time[filters[i]]}' if filters[i] else filters_[i]
            else:
                text = f'{filters_[i]}: {filters[i]}' if filters[i] else filters_[i]
            btn = InlineKeyboardButton(text=text, callback_data=i)
            builder.row(btn)
        if filter_exists:
            builder.row(InlineKeyboardButton(text='🧹сбросить фильтры', callback_data='no filters'))
        builder.row(
            InlineKeyboardButton(text='🔍искать', callback_data='find'),
            InlineKeyboardButton(text='🔙назад', callback_data='back')
        )
        return builder.as_markup()

    @staticmethod
    def time_markup():
        return InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='день', callback_data='day'),
                              InlineKeyboardButton(text='неделя', callback_data='week'),
                              InlineKeyboardButton(text='месяц', callback_data='month')],
                             [InlineKeyboardButton(text='3 месяца', callback_data='3 months'),
                              InlineKeyboardButton(text='год', callback_data='year')]]
        )

    @staticmethod
    def add_info_markup(added: dict):
        info = {'модель': 'model', 'цену': 'price', 'количество': 'amount', 'ссылку': 'link'}
        builder = InlineKeyboardBuilder()
        is_ready = True
        for key, val in info.items():
            if not val not in ('amount', 'link') and val not in added:
                is_ready = False
            icon = '✏' if added[val] else ''
            btn = InlineKeyboardButton(text=icon + key, callback_data=val)
            builder.row(btn)
        if is_ready:
            save_btn = InlineKeyboardButton(text='✅сохранить', callback_data='save')
            builder.row(save_btn, InlineKeyboardButton(text='🗑удалить', callback_data='delete'))
        else:
            builder.row(InlineKeyboardButton(text='🔙назад', callback_data='back'))

        return builder.as_markup()

    @staticmethod
    def build_comp_markup(added, edit: bool = False):
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
        builder = InlineKeyboardBuilder()
        is_ready = True
        for key, val in components.items():
            if val not in added:
                if val in ('title', 'cpu', 'gpu', 'motherboard', 'ram'):
                    is_ready = False
                btn = InlineKeyboardButton(text=key, callback_data=val)
            else:
                btn = InlineKeyboardButton(text='✏' + key, callback_data='edit_' + val)
            builder.row(btn)

        count = 0
        for comp in added:
            if comp not in components.values():
                btn = InlineKeyboardButton(text='✏' + comp, callback_data='edit_' + comp)
                builder.row(btn)
                count += 1

        if count < 5:
            builder.row(InlineKeyboardButton(text='➕добавить еще', callback_data='additional'))

        if is_ready:
            finish_btn = InlineKeyboardButton(text='✅сохранить', callback_data='edit_save' if edit else 'save')
            builder.row(finish_btn)

        builder.row(InlineKeyboardButton(text='🗑удалить сборку', callback_data='back'))

        return builder.as_markup()

    @staticmethod
    def build_final_markup(username):
        return InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='✏изменить', callback_data='change'),
                              InlineKeyboardButton(text='🕵️‍сохранить анонимно', callback_data='save_anonim'),
                              InlineKeyboardButton(text=f'😀сохранить от @{username}',
                                                   callback_data='save_with_username')]]
        )

    @staticmethod
    def my_pc_markup():
        return InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='✏изменить', callback_data='change')],
                             [InlineKeyboardButton(text='🔙назад', callback_data='back')]]
        )

    @staticmethod
    def my_assemblies(data: list[dict]):
        builder = InlineKeyboardBuilder()
        for item in data:
            if item['title']:
                builder.row(InlineKeyboardButton(text=item['title'], callback_data='assembly_' + str(item['id'])))
        builder.row(InlineKeyboardButton(text='🔙назад', callback_data='back'))
        return builder.as_markup()

    @staticmethod
    def show_pc_markup():
        return InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='фильтры', callback_data='back'),
                              InlineKeyboardButton(text='❤️', callback_data='like'), ],
                             [InlineKeyboardButton(text='<<<', callback_data='prev'),
                              InlineKeyboardButton(text='>>>', callback_data='next')]]
        )
