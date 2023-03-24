import requests

response_1 = requests.post('http://127.0.0.1:5000/user', json={'username': 'user_1', 'password': '1235'})
response_2 = requests.post('http://127.0.0.1:5000/adv',
                           json={'title': 'first adv', 'description': 'some descr', 'user_id': 1})
response_3 = requests.get('http://127.0.0.1:5000/adv/1')
response_4 = requests.patch('http://127.0.0.1:5000/adv/1',
                            json={'title': 'updated adv', 'description': 'updated descr'})
response_5 = requests.delete('http://127.0.0.1:5000/adv/1')

print(response_1.status_code)
print(response_1.json())
print(response_2.status_code)
print(response_2.json())
print(response_3.status_code)
print(response_3.json())
print(response_4.status_code)
print(response_4.json())
print(requests.get('http://127.0.0.1:5000/adv/1').json())
print(response_5.status_code)
print(response_5.json())
print(requests.get('http://127.0.0.1:5000/adv/1').json())
