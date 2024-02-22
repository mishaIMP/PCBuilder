import datetime as dt
import json
import logging
from functools import wraps

import requests


class Api:
    headers = {
        'Content-Type': 'application/json'
    }
    authorized = False

    def __init__(self, ip: str, username: str, password: str):
        self.IP = ip
        self.username = username
        self.password = password
        self.login_or_create_user(username, password)

    def login_user(self, username: str, password: str) -> bool:
        payload = json.dumps({'username': username, 'password': password})
        response = requests.post(self.IP + 'login', data=payload, headers=self.headers)
        if response.status_code == 200:
            self.headers['Authorization'] = response.json().get('jwt_token')
            self.authorized = True
            return True
        self.authorized = False
        return False

    def login_or_create_user(self, username: str, password: str) -> None:
        user_logged = self.login_user(username, password)
        if not user_logged:
            payload = json.dumps({'username': username, 'password': password})
            response = requests.post(self.IP + 'signup', data=payload, headers=self.headers)
            if response.status_code == 201:
                self.headers['Authorization'] = response.json().get('jwt_token')
                self.authorized = True
                return
        logging.critical('api error: impossible to log in')

    @staticmethod
    def keep_user_authorized(func):
        @wraps(func)
        def decorator(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            if not self.authorized:
                self.login_user(username=self.username, password=self.password)
                if not self.authorized:
                    logging.critical('api error: impossible to log in')
                return func(self, *args, **kwargs)
            return result
        return decorator

    @keep_user_authorized
    def init_pc(self) -> int | None:
        payload = json.dumps({
            "title": None,
            "author": None,
            "likes": None,
            "total_price": None
        })
        response1 = requests.post(self.IP + f'/info', data=payload, headers=self.headers)
        if response1.status_code == 201:
            info_id = response1.json()['id']
            return info_id
        self.authorized = False

    @keep_user_authorized
    def delete_pc(self, info_id: int = None, comp: str = None) -> None:
        if comp:
            response = requests.delete(self.IP + f'/comp/{info_id}?comps={comp}', headers=self.headers)
            if response.status_code == 202:
                return
        elif info_id:
            response = requests.delete(self.IP + f'/comp/{info_id}', headers=self.headers)
            if response.status_code in (202, 404):
                response2 = requests.delete(self.IP + f'/info/{info_id}', headers=self.headers)
                if response2.status_code == 202:
                    return
        self.authorized = False

    @keep_user_authorized
    def edit_component(self, comp: str, model: str, price: int, amount: int, info_id: int, link=None) -> None:
        payload = json.dumps({
            "component": comp,
            "model": model,
            "price": price,
            "amount": amount,
            "link": link
        })
        response = requests.patch(self.IP + f'/comp/{info_id}', data=payload, headers=self.headers)
        if response.status_code == 201:
            return
        self.authorized = False

    @keep_user_authorized
    def add_component(self, comp: str, model: str, price: int, amount: int, info_id: int, link: str = None) -> None:
        payload = json.dumps({
            "component": comp,
            "model": model,
            "model": model,
            "price": price,
            "amount": amount,
            "link": link
        })
        response = requests.post(self.IP + f'/comp/{info_id}', data=payload, headers=self.headers)
        if response.status_code == 201:
            return
        self.authorized = False

    @keep_user_authorized
    def patch_info(self, info_id: int, payload: dict) -> None:
        payload = json.dumps(payload)
        response = requests.patch(self.IP + f'/info/{info_id}', data=payload, headers=self.headers)
        if response.status_code == 204:
            return
        self.authorized = False

    def add_title(self, title: str, info_id: int) -> None:
        payload = {'title': title}
        return self.patch_info(info_id, payload)

    def like(self, info_id: int, likes: int) -> None:
        payload = {'likes': likes}
        return self.patch_info(info_id, payload)

    @keep_user_authorized
    def get_components(self, info_id: int, comp: str = None) -> dict | None:
        param = f'?comps={comp}' if comp else ''
        response = requests.get(self.IP + f'/comp/{info_id}{param}')
        if response.status_code == 200:
            return response.json()
        self.authorized = False

    @staticmethod
    def convert_time(date: str) -> dt.date:
        today = dt.date.today()
        if date == 'day':
            time_delta = dt.timedelta(days=1)
        elif date == 'week':
            time_delta = dt.timedelta(weeks=1)
        elif date == 'month':
            time_delta = dt.timedelta(days=30)
        elif date == '3 month':
            time_delta = dt.timedelta(days=90)
        else:
            time_delta = dt.timedelta(days=365)
        return today - time_delta

    @keep_user_authorized
    def get_list(self, filters_str: dict | None = None, params: list | None = None) -> dict | None:
        if filters_str:
            if filters_str.get('date', None):
                filters_str['date'] = self.convert_time(filters_str['date'])
        if params:
            filters_str['params'] = '-'.join(params)
        response = requests.get(self.IP + f'/info', params=filters_str, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        self.authorized = False

    def get_id_list(self, filters: dict) -> dict | None:
        return self.get_list(filters_str=filters, params=['id'])

    def get_title_and_id_list(self):
        return self.get_list(filters_str={'user': True}, params=['id', 'title'])

    @keep_user_authorized
    def final_save(self, info_id: int, info: dict) -> None:
        if 'info_id' in info:
            del info['info_id']
        payload = json.dumps(info)
        response = requests.put(self.IP + f'/info/{info_id}', data=payload, headers=self.headers)
        if response.status_code == 204:
            return
        self.authorized = False

    @keep_user_authorized
    def get_info(self, info_id: int) -> dict | None:
        response = requests.get(self.IP + f'/info/{info_id}')
        if response.status_code == 200:
            return response.json()
        self.authorized = False

    @keep_user_authorized
    def get_whole_pc(self, info_id: int) -> dict | None:
        components = self.get_components(info_id)
        if components:
            info = self.get_info(info_id)
            if info:
                components['info'] = info
                return components
        self.authorized = False
