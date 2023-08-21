import aiogram.utils.markdown as markdown

MAIN_MENU_TEXT = '/find - 🔍Найти сборку\n/add - ➕Добавить сборку\n/my - 🖥мои сборки'
ERROR_TEXT = 'произошла ошибка'


def display_pc(data: dict | dict) -> str:

    info = True if 'info' in data else False
        
    text = f"*{data['info']['title']}*\n" if info and data['info']['title'] else ''
     
    for comp in data['comps']['components']:
        if comp['model']:
            if comp['link']:
                model = f'[{comp["model"].upper()}]({comp["link"]})'
            else:
                model = comp["model"].upper()
            amount = f'\[x{comp["amount"]}\]' if comp['amount'] > 1 else ''
            text += f'*{model}* \- *{comp["price"]}* {amount}\n'
    if data['additional']['count']:
        text += f'_{"дополнительные комплектующие:"}_\n'
        for comp in data['additional']['components']:
            if comp['model']:
                if comp['link']:
                    model = f'[{comp["model"].upper()}]({comp["link"]})'
                else:
                    model = comp["model"].upper()
                amount = f'\[x{comp["amount"]}\]' if comp['amount'] > 1 else ''
                text += f'{comp["component"].upper()}: *{model}* \- *{comp["price"]}* {amount}\n'
            
    if info:
        text += f"всего \- *{data['info']['total_price']}* \t\t\t\t ❤{data['info']['likes']}❤\n"
        if data['info']['author']:
            text += f'by @{data["info"]["author"]}' 
        
    return text


def calculate_total_price(data: dict | dict) -> int:
    total_price = 0
    for comp in data['comps']['components']:
        if comp['price']:
            total_price += comp['price'] * comp.get('amount', 1)
    if data['additional']['count']:
        for comp in data['additional']['components']:
            if comp['price']:
                total_price += comp['price'] * comp.get('amount', 1)
    return total_price


def get_comps(data: dict) -> list:
    components = []
    print(data)
    for comp in data['comps']['components']:
        components.append(comp['component'])
    if data['additional']['count']:
        for comp in data['additional']['components']:
            components.append(comp['component'])
    return components
