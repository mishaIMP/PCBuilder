import requests
import json


class Api:
    def __init__(self, ip):
        self.IP = ip

    headers = {
        'Content-Type': 'application/json'
    }

    def add_new_user(self, username: str) -> object | None:
        payload = json.dumps({'username': username})
        response = requests.post(self.IP + '/users', data=payload, headers=self.headers)
        if response.status_code == 201:
            return response.json()
        else:
            return None

    def init_pc(self, user_id: int = 1) -> object | None:
        payload = json.dumps({"user_id": user_id})
        response = requests.post(self.IP + f'/comp', data=payload, headers=self.headers)
        if response.status_code == 201:
            return response.json()
        else:
            return None

    def delete_pc(self, comp_id: int, comp: str = None) -> bool:
        param = f'?comp={comp}' if comp else ''
        response = requests.delete(self.IP + f'/comp/{comp_id}{param}')
        if response.status_code == 202:
            return True
        else:
            return False

    def add_comp(self, comp: str, model: str, price: int, amount: int, comp_id: int, link=None) -> bool:
        payload = json.dumps({
            "comp_id": comp_id,
            "comp": comp,
            "model": model,
            "price": price,
            "amount": amount,
            "link": link
        })
        response = requests.put(self.IP + '/comp', data=payload, headers=self.headers)
        if response.status_code == 200:
            return True
        else:
            return False

    def add_title(self, title: str, comp_id: int) -> bool:
        payload = json.dumps({'title': title, 'comp_id': comp_id})
        response = requests.post(self.IP + '/title', data=payload, headers=self.headers)
        if response.status_code == 201:
            return True
        else:
            return False

    def get_pc(self, comp_id: int):
        response = requests.get(self.IP + f'/comp/{comp_id}')
        if response.status_code == 200:
            return response.json()
        else:
            return False
