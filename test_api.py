import requests

base = 'http://127.0.0.1:8000'

req = {
    'description': 'There is a large water leak near the main road and traffic is affected',
    'location': 'Main Road'
}
res = requests.post(f'{base}/complaints', json=req)
print('POST', res.status_code)
print(res.json())
res2 = requests.get(f'{base}/complaints')
print('GET', res2.status_code)
print(res2.json())
res3 = requests.get(f'{base}/stats')
print('STATS', res3.status_code)
print(res3.json())
