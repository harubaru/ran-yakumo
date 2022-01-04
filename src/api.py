import requests
import json

class Sukima_API():
    def __init__(self, ip: str, username: str, password: str): 
        self.ip = ip
        try:
            self.auth(username, password)
        except:
            self.token = None

    def auth(self, username: str, password: str):
        try:
            r = self.post(f'http://{self.ip}:8000/api/v1/users/token', data={'username':username,'password':password}, timeout=1.0)
        except Exception as e:
            raise e
        if r.status_code == 200:
            self.token = r.json()['access_token']
        else:
            raise Exception('Unable to authenticate to Sukima servers.', r.json())
    
    def post(self, url, data, auth = None, timeout=20.0):
        headers = None
        if auth:
            headers = {'Authorization': f'Bearer {auth}'}
        r = requests.post(url=url, data=data, headers=headers, timeout=timeout)
        return r
    
    def get(self, url, auth = None, timeout=5.0):
        headers = None
        if auth:
            headers = {'Authorization': f'Bearer {auth}'}
        r = requests.get(url=url, headers=headers, timeout=timeout)
        return r
    
    def healthcheck(self):
        r = self.get(f'http://{self.ip}:8000/')
        if r.status_code == 200:
            return True
        else:
            return False

    def get_models(self):
        r = self.get(f'http://{self.ip}:8000/api/v1/models')
        if r.status_code == 200:
            # model is returned as a dict, which is formatted as {'models':{'c1-6b':{'ready':True}}}
            # return dict as a list of model names
            return list(r.json()['models'].keys())
        else:
            raise Exception('Unable to fetch models.')

    def generate(self, args):
        r = self.post(f'http://{self.ip}:8000/api/v1/models/generate', data=json.dumps(args), auth=self.token)
        if r.status_code == 200:
            return r.json()['completion']['text'][len(args['prompt']):]
        else:
            raise Exception('Unable to generate text.', r.json())
