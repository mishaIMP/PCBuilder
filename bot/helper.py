from aiogram.utils.markdown import hbold, hlink, hitalic


def show_pc(data):
    text = f"{hbold(data['title'].upper())}\n\n"
    for key, val in data['components'].items():
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

    text += f"-- {data['date'][:4]} . {data['date'][5:7]} . {data['date'][8:10]} --\t\t"
    if data['username'] != 'default':
        text += hitalic(f'by @{data["username"]}')
    return text
