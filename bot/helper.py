from aiogram.utils.markdown import hbold, hlink, hitalic


def show_pc(data: dict | object) -> str:
    if 'info' in data:
        info = True
        
    text = data['info']['title'] + '\n' if info else '' 
     
    for comp in data['comps']['components']:
        if comp['model']:
            if comp['link']:
                model = f'{hlink(comp["model"].upper(), comp["link"])}'
            else:
                model = comp["model"].upper()
            text += f'{model} - {comp["price"]} [x{comp["amount"]}]\n'
    if data['additional']['count']:
        text += f'{hitalic("дополнительные комплектующие:")}\n'
        for comp in data['additional']['components']:
            if comp['link']:
                model = f'{hlink(comp["model"].upper(), comp["link"])}'
            else:
                model = comp["model"].upper()
            text += f'{hitalic(comp["component"].upper())}: {model} - {comp["price"]} [x{comp["amount"]}]\n'
            
    if info:
        text += f"всего - {data['info']['total_price']} ~~ ❤️{data['info']['likes']}❤️ ~~\n"
        if data['info']['author']:
            text += f'by @{data["info"]["author"]}' 
        
    return text


def calculate_total_price(data: dict | object) -> int:
    total_price = 0
    for comp in data['comps']['components']:
        if comp['price']:
            total_price += comp['price']
    if data['additional']['count']:
        for comp in data['additional']['components']:
            if comp['price']:
                total_price += comp['price']
    return total_price

def get_comps(data: dict | object) -> list:
    components = []
    for comp in data['comps']['components']:
        components.append(comp['components'])
    if data['additional']['count']:
        for comp in data['additional']['components']:
            components.append(comp['component'])
    return components
