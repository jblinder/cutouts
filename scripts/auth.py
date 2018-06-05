import requests
response = requests.post(
  'https://www.muckrock.com/api_v1/token-auth/',
  data={
    'username': 'nullpanda',
    'password': 'password'
  }
)
token = response.json()['token']
print(token)