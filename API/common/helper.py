from API.common.model import Prices, Components, Amounts, Links, Additional, PublicInfo

COMPONENTS = ['cpu', 'gpu', 'motherboard', 'ram', 'case', 'storage', 'psu', 'culler', 'fan']


def convert_comp_data(comp: Components, price: Prices, amount: Amounts, link: Links, additional: list[Additional],
                      specific: str | None = None) -> dict:
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


def is_valid_params(params: str | None) -> bool:
    if params:
        for param in params.split('-'):
            if param not in ('id', 'likes', 'total_price', 'author', 'date', 'title', 'user_id', 'comp_id'):
                return False
    return True


def convert_info(tables: list[PublicInfo] | PublicInfo, params: str | None) -> None | dict:
    if params:
        params = params.split('-')
    else:
        params = ['id', 'likes', 'total_price', 'author', 'date', 'title', 'user_id', 'comp_id']

    def convert(table_: PublicInfo) -> dict:
        res = {}
        for param in params:
            if param == 'comp_id':
                if table_.components:
                    res[param] = table_.components[0].id
            elif param == 'date':
                res[param] = str(table_.__getattribute__(param))
            else:
                res[param] = table_.__getattribute__(param)
        return res

    if type(tables) == list:
        result = {'data': []}
        for table in tables:
            result['data'].append(convert(table))
    else:
        result = convert(tables)

    return result




