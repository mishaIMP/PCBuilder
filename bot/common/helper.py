def display_pc(data: dict) -> str:
    info = True if data and 'info' in data else False

    text = f"<b>{data['info']['title']}\n</b>" if info and data['info']['title'] else ''

    def display_component(component):
        if component['model']:
            if component['link']:
                model = f'<a href="{component["link"]}">{component["model"].upper()}</a>'
            else:
                model = component["model"].upper()
            amount = f' [x{component["amount"]}]' if component['amount'] > 1 else ''
            return f'{component["component"].upper()}: <b>{model} - {component["price"]}</b>{amount}\n'

    for comp in data['comps']['components']:
        text += display_component(comp)
    if data['additional']['count']:
        text += f'<i>{"дополнительные комплектующие:"}</i>\n'
        for comp in data['additional']['components']:
            text += display_component(comp)

    if info:
        text += f"<u><b>всего - {data['info']['total_price']}</b></u>\t\t\t\t ❤{data['info']['likes']}❤"
        if data['info']['author']:
            text += f'\nавтор: @{data["info"]["author"]}'

    return text


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
    if data['comps']['count']:
        component = data['comps']['components'][0]
    elif data['additional']['count']:
        component = data['additional']['components'][0]
    return component
