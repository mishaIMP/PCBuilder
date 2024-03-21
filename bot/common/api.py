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
        if response.ok:
            self.headers['Authorization'] = response.json().get('jwt_token')
            self.authorized = True
            return True
        self.authorized = response.status_code != 403
        return False

    def login_or_create_user(self, username: str, password: str) -> None:
        user_logged = self.login_user(username, password)
        if not user_logged:
            payload = json.dumps({'username': username, 'password': password})
            response = requests.post(self.IP + 'signup', data=payload, headers=self.headers)
            if response.ok:
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
        if response1.ok:
            info_id = response1.json()['id']
            return info_id
        self.authorized = response1.status_code == 403

    @keep_user_authorized
    def delete_pc(self, info_id: int = None, comp: str = None) -> None:
        if comp:
            response = requests.delete(self.IP + f'/comp/{info_id}?comps={comp}', headers=self.headers)
            if response.ok:
                return
        elif info_id:
            response = requests.delete(self.IP + f'/comp/{info_id}', headers=self.headers)
            if response.ok:
                response2 = requests.delete(self.IP + f'/info/{info_id}', headers=self.headers)
                if response2.status_code == 202:
                    return
                self.authorized = response2.status_code != 403

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
        if response.ok:
            return
        self.authorized = response.status_code != 403

    @keep_user_authorized
    def add_component(self, comp: str, model: str, price: int, amount: int, info_id: int, link: str = None) -> None:
        payload = json.dumps({
            "component": comp,
            "model": model,
            "price": price,
            "amount": amount,
            "link": link
        })
        response = requests.post(self.IP + f'/comp/{info_id}', data=payload, headers=self.headers)
        if response.ok:
            return
        self.authorized = response.status_code != 403

    @keep_user_authorized
    def patch_info(self, info_id: int, payload: dict) -> None:
        payload = json.dumps(payload)
        response = requests.patch(self.IP + f'/info/{info_id}', data=payload, headers=self.headers)
        if response.ok:
            return
        self.authorized = response.status_code != 403

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
        if response.ok:
            return response.json()
        self.authorized = response.status_code != 403

    @keep_user_authorized
    def get_list(self, filters: dict | None = None, params: list | None = None) -> dict | None:
        if params:
            filters['params'] = '-'.join(params)
        response = requests.get(self.IP + f'/info', params=filters, headers=self.headers)
        if response.ok:
            return response.json()
        self.authorized = response.status_code != 403

    def get_id_list(self, filters: dict) -> dict | None:
        return self.get_list(filters=filters, params=['id'])

    def get_title_and_id_list(self):
        return self.get_list(filters={'user': True}, params=['id', 'title'])

    @keep_user_authorized
    def get_info(self, info_id: int) -> dict | None:
        response = requests.get(self.IP + f'/info/{info_id}')
        if response.ok:
            return response.json()
        self.authorized = response.status_code != 403

    @keep_user_authorized
    def get_whole_pc(self, info_id: int) -> dict | None:
        components = self.get_components(info_id)
        if components:
            info = self.get_info(info_id)
            if info:
                components['info'] = info
                return components

    @keep_user_authorized
    def calculate_total_price(self, info_id: int) -> None:
        response = requests.patch(self.IP + f'/info/total_price/{info_id}', headers=self.headers)
        if response.ok:
            return
        self.authorized = response.status_code != 403
