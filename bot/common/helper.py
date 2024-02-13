def display_pc(data: dict | dict) -> str:
    info = True if 'info' in data else False

    text = f"*{data['info']['title']}*\n" if info and data['info']['title'] else ''

    def display_component(component):
        if component['model']:
            if component['link']:
                model = f'[{component["model"].upper()}]({component["link"]})'
            else:
                model = comp["model"].upper()
            amount = f' \[x{component["amount"]}\]' if component['amount'] > 1 else ''
            return f'{component["component"].upper()}: *{model} \- {component["price"]}*{amount}\n'

    for comp in data['comps']['components']:
        text += display_component(comp)
    if data['additional']['count']:
        text += f'_{"дополнительные комплектующие:"}_\n'
        for comp in data['additional']['components']:
            text += display_component(comp)

    if info:
        text += f"__*всего \- {data['info']['total_price']}*__ \t\t\t\t ❤{data['info']['likes']}❤\n"
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
    for comp in data['comps']['components']:
        components.append(comp['component'])
    if data['additional']['count']:
        for comp in data['additional']['components']:
            components.append(comp['component'])
    return components


def get_component(data: dict) -> dict | None:
    component = None
    if data.get('comps', {}).get('count', None):
        component = data['comps']['components'][0]
    elif data.get('additional', {}).get('count', None):
        component = data['additional']['components'][0]
    return component
