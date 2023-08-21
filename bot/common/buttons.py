from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class Buttons:
    @staticmethod
    def start_markup():
        start_markup = InlineKeyboardMarkup(row_width=3)
        start_markup.add(
            InlineKeyboardButton('🔍', callback_data='find'),
            InlineKeyboardButton('➕', callback_data='add'),
            InlineKeyboardButton('🖥', callback_data='my')
        )
        return start_markup

    @staticmethod
    def back_markup():
        back_markup = InlineKeyboardMarkup()
        back_markup.add(InlineKeyboardButton('🔙назад', callback_data='back'))
        return back_markup

    @staticmethod
    def skip_markup():
        skip_markup = InlineKeyboardMarkup()
        skip_markup.add(InlineKeyboardButton('⏭пропустить', callback_data='skip'))
        return skip_markup

    @staticmethod
    def filter_markup(filters: dict):
        filter_markup = InlineKeyboardMarkup()
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
            btn = InlineKeyboardButton(text, callback_data=i)
            filter_markup.add(btn)
        if filter_exists:
            filter_markup.add(InlineKeyboardButton('🧹сбросить фильтры', callback_data='no filters'))
        filter_markup.add(
            InlineKeyboardButton('🔍искать', callback_data='find'),
            InlineKeyboardButton('🔙назад', callback_data='back')
        )
        return filter_markup

    @staticmethod
    def time_markup():
        time_markup = InlineKeyboardMarkup()
        time_markup.add(
            InlineKeyboardButton('день', callback_data='day'),
            InlineKeyboardButton('неделя', callback_data='week'),
            InlineKeyboardButton('месяц', callback_data='month'),
            InlineKeyboardButton('3 месяца', callback_data='3 months'),
            InlineKeyboardButton('год', callback_data='year')
        )
        return time_markup

    @staticmethod
    def add_info_markup(added: dict):
        info = {'модель': 'model', 'цену': 'price', 'количество': 'amount', 'ссылку': 'link'}
        info_markup = InlineKeyboardMarkup(row_width=1)
        is_ready = True
        for key, val in info.items():
            if not val not in ('amount', 'link') and val not in added:
                is_ready = False
            icon = '✏' if added[val] else ''
            btn = InlineKeyboardButton(icon + key, callback_data=val)
            info_markup.add(btn)
        if is_ready:
            save_btn = InlineKeyboardButton('✅сохранить', callback_data='save')
            info_markup.add(save_btn, InlineKeyboardButton('🗑удалить', callback_data='delete'))
        else:
            info_markup.add(InlineKeyboardButton('🔙назад', callback_data='back'))

        return info_markup

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
        comp_markup = InlineKeyboardMarkup(row_width=2)
        is_ready = True
        for key, val in components.items():
            if val not in added:
                if val in ('title', 'cpu', 'gpu', 'motherboard', 'ram'):
                    is_ready = False
                btn = InlineKeyboardButton(key, callback_data=val)
            else:
                btn = InlineKeyboardButton('✏' + key, callback_data='edit_' + val)
            comp_markup.add(btn)

        count = 0
        for comp in added:
            if comp not in components.values():
                btn = InlineKeyboardButton('✏' + comp, callback_data='edit_' + comp)
                comp_markup.add(btn)
                count += 1

        if count < 5:
            comp_markup.add(InlineKeyboardButton('➕добавить еще', callback_data='additional'))

        if is_ready:
            finish_btn = InlineKeyboardButton('✅сохранить', callback_data='edit_save' if edit else 'save')
            comp_markup.add(finish_btn)

        comp_markup.add(InlineKeyboardButton('🗑удалить сборку', callback_data='back'))

        return comp_markup

    @staticmethod
    def build_final_markup(username, back: bool = False):
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton('✏изменить', callback_data='change'),
            InlineKeyboardButton('🕵️‍сохранить анонимно', callback_data='save_anonim'),
            InlineKeyboardButton(f'😀сохранить от @{username}', callback_data='save_with_username')
        )
        if back:
            markup.add(InlineKeyboardButton('🔙назад', callback_data='back'))
        return markup
    
    @staticmethod
    def my_assemblies(data: list[dict]):
        markup = InlineKeyboardMarkup(row_width=1)
        for item in data:
            if item['title']:
                markup.add(InlineKeyboardButton(item['title'], callback_data='assembly_' + str(item['id'])))
        markup.add(InlineKeyboardButton('🔙назад', callback_data='back'))
        return markup
    
    @staticmethod
    def show_pc_markup():
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton('фильтры', callback_data='back'),
            InlineKeyboardButton('❤️', callback_data='like'),
            InlineKeyboardButton('<<<', callback_data='prev'),
            InlineKeyboardButton('>>>', callback_data='next')
            )
        return markup
