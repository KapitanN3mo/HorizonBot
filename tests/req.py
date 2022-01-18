import requests
import json

jdata = {'username': 'test', 'password': 'qwerty'}
resp = requests.post('http://127.0.0.1:5000/api/login', json=jdata)
