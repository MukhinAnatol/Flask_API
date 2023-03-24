import requests

response_1 = requests.post('http://127.0.0.1:5000/adv',
                           json={'title': 'first adv', 'description': 'some descr', 'user_id': 1})
response_2 = requests.get('http://127.0.0.1:5000/adv/1')

#response_1 = requests.post('http://127.0.0.1:5000/adv',
#                          json={'username': 'user_2', 'password': '1235'})

print(response_1.status_code)
print(response_1.json())
print(response_2.status_code)
print(response_2.json())