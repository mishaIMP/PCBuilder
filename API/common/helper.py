from typing import Iterable, Sized

from sqlalchemy_utils import InstrumentedList

from API.common.model import BuildInfo

COMPONENTS = ['cpu', 'gpu', 'motherboard', 'ram', 'case', 'storage', 'psu', 'culler', 'fan']


def is_valid_params(params: str | None) -> bool:
    if params:
        for param in params.split('-'):
            if param not in ('id', 'likes', 'total_price', 'author', 'date', 'title', 'user_id'):
                return False
    return True


def convert_info(rows: InstrumentedList | BuildInfo, params: str | None) -> None | dict:
    if params:
        params = params.split('-')
    else:
        params = ['id', 'likes', 'total_price', 'author', 'date', 'title', 'user_id']

    def convert(table_: BuildInfo) -> dict:
        res = {}
        for param in params:
            if param == 'date':
                res[param] = str(table_.__getattribute__(param))
            else:
                res[param] = table_.__getattribute__(param)
        return res

    if isinstance(rows, (Iterable, Sized)):
        result = {'count': len(rows), 'data': []}
        for row in rows:
            result['data'].append(convert(row))
    else:
        result = convert(rows)

    return result


def is_valid_request_data(data: list | None) -> bool:
    if not data or type(data) is not list:
        return False
    for pc in data:
        if type(pc) is not dict:
            return False
        for item in ('component', 'model', 'price', 'amount', 'link'):
            if item not in pc:
                return False
    return True
