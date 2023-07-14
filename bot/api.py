import requests
import json


class Api:
    def __init__(self, ip):
        self.IP = ip

    headers = {
        'Content-Type': 'application/json'
    }

    def user_exists(self, username: str) -> object | None:
        response = requests.get(self.IP + f'/users?username={username}')
        if response.status_code == 200:
            return response.json()
        return False

    def add_new_user(self, username: str) -> object | None:
        payload = json.dumps({'username': username})
        response = requests.post(self.IP + '/users', data=payload, headers=self.headers)
        if response.status_code == 201:
            return response.json()
        return None

    def init_pc(self, user_id: int = 1) -> object | None:
        payload = json.dumps({"user_id": user_id})
        response1 = requests.post(self.IP + f'/info', data=payload, headers=self.headers)
        if response1.status_code == 201:
            info_id = response1.json()['id']
            payload = json.dumps({'info_id': info_id})
            response2 = requests.post(self.IP + f'/comp', data=payload, headers=self.headers)
            if response2.status_code == 201:
                return dict(info_id=info_id, **response2.json())
        return None

    def delete_pc(self, comp_id: int, info_id: int = None, comp: str = None) -> bool:
        if comp:
            response = requests.delete(self.IP + f'/comp/{comp_id}?comps={comp}')
            if response.status_code == 202:
                return True
        elif info_id:
            response = requests.delete(self.IP + f'/comp/{comp_id}')
            if response.status_code == 202:
                response2 = requests.delete(self.IP + f'/info/{info_id}')
                if response2.status_code == 202:
                    return True
        return False

    def add_comp(self, comp: str, model: str, price: int, amount: int, comp_id: int, link=None) -> bool:
        payload = json.dumps({
            "comp": comp,
            "model": model,
            "price": price,
            "amount": amount,
            "link": link
        })
        response = requests.patch(self.IP + f'/comp/{comp_id}', data=payload, headers=self.headers)
        if response.status_code == 204:
            return True
        return False

    def add_title(self, title: str, info_id: int) -> bool:
        payload = json.dumps({'title': title})
        response = requests.patch(self.IP + f'/info/{info_id}', data=payload, headers=self.headers)
        if response.status_code == 204:
            return True
        return False

    def get_pc(self, comp_id: int, comp: str = None):
        param = f'?comps={comp}' if comp else ''
        response = requests.get(self.IP + f'/comp/{comp_id}{param}')
        if response.status_code == 200:
            return response.json()
        return None

    def final_save(self, info_id: int, total_price: int, author: str | None = None):
        payload = json.dumps({
            'total_price': total_price,
            'author': author
        })
        response = requests.patch(self.IP + f'/info/{info_id}', data=payload, headers=self.headers)
        if response.status_code == 204:
            return True
        return False
