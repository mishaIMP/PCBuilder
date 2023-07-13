from API.common.model import Prices, Components, Amounts, Links, Additional


COMPONENTS = ['cpu', 'gpu', 'motherboard', 'ram', 'case', 'storage', 'psu', 'culler', 'fan']


def convert_data(comp: Components, price: Prices, amount: Amounts, link: Links, additional: list[Additional],
                 specific: str | None = None):
    if specific:
        result = {
            'model': comp.__getattribute__(specific),
            'price': price.__getattribute__(specific),
            'amount': amount.__getattribute__(specific),
            'link': link.__getattribute__(specific)
        }
    else:
        result = {'components': {}}
        for component in COMPONENTS:
            element = {component: {
                'model': comp.__getattribute__(component),
                'price': price.__getattribute__(component),
                'amount': amount.__getattribute__(component),
                'link': link.__getattribute__(component)
            }}
            result['components'].update(element)
        if additional:
            result.update({'additional': {
                'count': len(additional),
                'items': []
            }})
            for el in additional:
                element = {
                    'comp': el.comp,
                    'model': el.model,
                    'price': el.price,
                    'amount': el.amount,
                    'link': el.link
                }
                result['additional']['items'].append(element)

    return result


def is_valid_params(params: str):
    for param in params.split('-'):
        if param not in ('likes', 'total_price', 'author', 'date', 'title'):
            return False
    return True

