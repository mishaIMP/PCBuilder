from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class Buttons:
    start_markup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='🔍', callback_data='find'),
                          InlineKeyboardButton(text='➕', callback_data='add'),
                          InlineKeyboardButton(text='🖥', callback_data='my')]]
    )
    back_to_main_menu = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='в главное меню', callback_data='main_menu')]])

    back_to_filters = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='перейти к фильтрам', callback_data='to_filters')]]
    )

    show_pc_markup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='👍', callback_data='like'),
                          InlineKeyboardButton(text='👎', callback_data='dislike')],
                         [InlineKeyboardButton(text='➡', callback_data='next')],
                         [InlineKeyboardButton(text='фильтры', callback_data='to_filters')]]
    )

    back_markup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='🔙назад', callback_data='back')]]
    )

    skip_markup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='⏭пропустить', callback_data='skip')]]
    )

    time_markup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='день', callback_data='day'),
                          InlineKeyboardButton(text='неделя', callback_data='week'),
                          InlineKeyboardButton(text='месяц', callback_data='month')],
                         [InlineKeyboardButton(text='3 месяца', callback_data='3 months'),
                          InlineKeyboardButton(text='год', callback_data='year')]]
    )

    my_pc_markup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='✏изменить', callback_data='change')],
                         [InlineKeyboardButton(text='🔙назад', callback_data='back')]]
    )

    @staticmethod
    def filter_markup(filters: dict) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        filters_ = {
            'min_price': '💴min стоимость',
            'max_price': '💵max стоимость',
            'title': '📝название',
            'author': '🤵‍автор'
        }
        filter_exists = False
        for i in filters_:
            if filters[i]:
                filter_exists = True
            text = f'{filters_[i]}: {filters[i]}' if filters[i] else filters_[i]
            btn = InlineKeyboardButton(text=text, callback_data=i)
            builder.row(btn)
        if filter_exists:
            builder.row(InlineKeyboardButton(text='🧹сбросить фильтры', callback_data='reset_filters'))
        builder.row(
            InlineKeyboardButton(text='🔍искать', callback_data='find'),
            InlineKeyboardButton(text='🔙назад', callback_data='back')
        )
        return builder.as_markup()

    @staticmethod
    def add_info_markup(added: dict) -> InlineKeyboardMarkup:
        info = {'модель': 'model', 'цена': 'price', 'количество': 'amount', 'ссылка': 'link'}
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
    def comp_markup(added=None) -> InlineKeyboardMarkup:
        if not added:
            added = []
        components = {
            'название': 'title',
            'процессор': 'cpu',
            'материнскую плату': 'motherboard',
            'оперативную память': 'ram',
            'видеокарту': 'gpu',
            'HDD/SSD': 'storage',
            'корпус': 'case',
            'блок питания': 'psu',
            'охлаждение процессора': 'culler'
        }
        builder = InlineKeyboardBuilder()
        is_ready = True
        for key, val in components.items():
            if val not in added:
                if val in ('title', 'cpu', 'motherboard', 'ram'):
                    is_ready = False
                btn = InlineKeyboardButton(text=key, callback_data=val)
            else:
                btn = InlineKeyboardButton(text='✏' + key, callback_data='edit_' + val)
            builder.row(btn)

        additional_components = {
            'fan': 'корпусные вентиляторы',
            'sound_card': 'звуковую карту',
            'lan_card': 'сетевую карту',
            'gpu_holder': 'даржатель для видеокарты',
            'more_storage': 'дополнительные HDD/SSD'
        }
        count = 0
        for comp in added:
            if comp in additional_components.keys():
                btn = InlineKeyboardButton(text='✏' + additional_components[comp], callback_data='edit_' + comp)
                builder.row(btn)
                count += 1

        if count < 5:
            builder.row(InlineKeyboardButton(text='➕добавить еще', callback_data='additional'))

        if is_ready:
            finish_btn = InlineKeyboardButton(text='✅сохранить', callback_data='save')
            builder.row(finish_btn)

        builder.row(InlineKeyboardButton(text='🗑удалить сборку', callback_data='back'))

        return builder.as_markup()

    @staticmethod
    def additional_comp_markup(added=None) -> InlineKeyboardMarkup:
        if not added:
            added = []
        additional_components = {
            'fan': 'корпусные вентиляторы',
            'sound_card': 'звуковую карту',
            'lan_card': 'сетевую карту',
            'gpu_holder': 'даржатель для видеокарты',
            'more_storage': 'дополнительные HDD/SSD'
        }
        builder = InlineKeyboardBuilder()
        for component in additional_components:
            if component not in added:
                builder.row(InlineKeyboardButton(text=additional_components[component], callback_data=component))
        return builder.as_markup()

    @staticmethod
    def final_markup() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='✏изменить', callback_data='change')],
                             [InlineKeyboardButton(text='🕵️‍указать автора сборки', callback_data='set_author')],
                             [InlineKeyboardButton(text='❌не указывать', callback_data='skip')]]
        )

    @staticmethod
    def my_builds(data: list[dict]) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for build in data:
            if build['title']:
                builder.row(
                    InlineKeyboardButton(text=build['title'],
                                         callback_data='assembly_' + str(build['id']))
                )
        builder.row(InlineKeyboardButton(text='🔙назад', callback_data='back'))
        return builder.as_markup()
