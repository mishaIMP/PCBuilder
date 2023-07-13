from aiogram.utils.markdown import hbold, hlink, hitalic


def show_pc(data):
    text = f"{hbold(data['title'].upper())}\n\n"
    for key, val in data['components'].items():
        if all((val['model'], val['price'], val['amount'])):
            if val['link']:
                model = f'{hlink(val["model"].upper(), val["link"])}'
            else:
                model = val["model"].upper()
            text += f'{model} - {val["price"]} [x{val["amount"]}]\n'
    if 'additional' in data:
        text += f'{hitalic("дополнительные комплектующие:")}\n'
        for i, comp in enumerate(data['additional']['items']):
            if comp['link']:
                model = f'{hlink(comp["model"].upper(), comp["link"])}'
            else:
                model = comp["model"].upper()
            text += f'{hitalic(comp["comp"].upper())}: {model} - {comp["price"]} [x{comp["amount"]}]\n'
    return text
