from API.common.model import Components, PublicInfo

COMPONENTS = ['cpu', 'gpu', 'motherboard', 'ram', 'case', 'storage', 'psu', 'culler', 'fan']


def is_valid_params(params: str | None) -> bool:
    if params:
        for param in params.split('-'):
            if param not in ('id', 'likes', 'total_price', 'author', 'date', 'title', 'user_id'):
                return False
    return True


def convert_info(tables: list[PublicInfo] | PublicInfo, params: str | None) -> None | dict:
    if params:
        params = params.split('-')
    else:
        params = ['id', 'likes', 'total_price', 'author', 'date', 'title', 'user_id']

    def convert(table_: PublicInfo) -> dict:
        res = {}
        for param in params:
            if param == 'date':
                res[param] = str(table_.__getattribute__(param))
            else:
                res[param] = table_.__getattribute__(param)
        return res

    if type(tables) == list:
        result = {'count': len(tables), 'data': []}
        for table in tables:
            result['data'].append(convert(table))
    else:
        result = convert(tables)

    return result


def is_valid_request_data(data: list) -> bool:
    if not data or type(data) != list:
        return False
    for pc in data:
        if type(pc) != dict:
            return False
        for item in ('component', 'model', 'price', 'amount', 'link'):
            if item not in pc:
                return False
    return True




