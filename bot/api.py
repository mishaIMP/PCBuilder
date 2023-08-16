import requests
import json
import datetime as dt

        
class Api():
    def __init__(self, ip: str):
        self.IP = ip

    headers = {
        'Content-Type': 'application/json'
    }

    def user_exists(self, username: str) -> object | None:
        response = requests.get(self.IP + f'/users?username={username}')
        if response.status_code == 200:
            return response.json()
        return None
# params=params
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
            return dict(info_id=info_id)
        return None

    def delete_pc(self, info_id: int = None, comp: str = None) -> bool:
        if comp:
            response = requests.delete(self.IP + f'/comp/{info_id}?comps={comp}')
            if response.status_code == 202:
                return True
        elif info_id:
            response = requests.delete(self.IP + f'/comp/{info_id}')
            if response.status_code == 202:
                response2 = requests.delete(self.IP + f'/info/{info_id}')
                if response2.status_code == 202:
                    return True
        return False

    def edit_component(self, comp: str, model: str, price: int, amount: int, info_id: int, link=None) -> bool:
        payload = json.dumps({
            "component": comp,
            "model": model,
            "price": price,
            "amount": amount,
            "link": link
        })
        response = requests.patch(self.IP + f'/comp/{info_id}', data=payload, headers=self.headers)
        if response.status_code == 201:
            return True
        return False
    
    def add_component(self, comp: str, model: str, price: int, amount: int, info_id: int, link: str = None) -> bool:
        payload = json.dumps({
            "component": comp,
            "model": model,
            "price": price,
            "amount": amount,
            "link": link
        })
        response = requests.post(self.IP + f'/comp/{info_id}', data=payload, headers=self.headers)
        if response.status_code == 201:
            return True
        return False

    def patch_info(self, info_id: int, payload: dict) -> bool:
        payload = json.dumps(payload)
        response = requests.patch(self.IP + f'info/{info_id}', data=payload, headers=self.headers)
        if response.status_code == 204:
            return True
        return False
    
    def add_title(self, title: str, info_id: int) -> bool:
        payload = {'title': title}
        return self.patch_info(info_id, payload)
        
    def like(self, info_id: int, likes: int) -> bool:
        payload = {'likes': likes}
        return self.patch_info(info_id, payload)
    
    def get_components(self, info_id: int, comp: str = None) -> object | None:
        param = f'?comps={comp}' if comp else ''
        response = requests.get(self.IP + f'/comp/{info_id}{param}')
        if response.status_code == 200:
            return response.json()
        return None
    
    @staticmethod
    def convert_time(date: str) -> dt.date:
        today = dt.date.today()
        if date == 'day':
            timedalta = dt.timedelta(days=1)
        elif date == 'week':
            timedalta =  dt.timedelta(weeks=1)
        elif date == 'month':
            timedalta =  dt.timedelta(days=30)
        elif date == '3 month':
            timedalta =  dt.timedelta(days=90)
        else:
            timedalta =  dt.timedelta(days=365)
        return today - timedalta
    
    def get_list(self, filters_str: dict | None = None, params: list | None = None) -> object | None:
        if filters_str:
            if filters_str.get('date', None):
                filters_str['date'] = self.convert_time(filters_str['date'])
            
            filters_str = ''.join([f'&{i[0]}={i[1]}' for i in filters_str.items() if i[1]])
        params_ = '-'.join(params) if params else 'all'
        response = requests.get(self.IP + f'/info?params={params_}{filters_str}', headers=self.headers)
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_id_list(self, filters: dict) -> object | None:
        return self.get_list(filters_str=filters, params=['id'])
    
    def get_title_and_id_list(self, user_id: int):
        return self.get_list(self, filters_str={'user_id': user_id}, params=['id', 'title'])
        
    def final_save(self, info_id: int, total_price: int, author: str | None = None) -> bool:
        payload = json.dumps({
            'total_price': total_price,
            'author': author
        })
        response = requests.patch(self.IP + f'/info/{info_id}', data=payload, headers=self.headers)
        if response.status_code == 204:
            return True
        return False
    
    def get_info(self, info_id: int) -> object | None:
        response = requests.get(self.IP + f'/info{info_id}')
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_whole_pc(self, info_id: int) -> object | None:
        components = self.get_components(info_id)
        if components:
            info = self.get_info(info_id)
            if info:
                components['info'] = info
                return components
        return None