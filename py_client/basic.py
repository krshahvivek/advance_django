import requests

# endpoint = "https://httpbin.org/anything"
endpoint = "http://localhost:8000/api/post/"     #http://127.0.0.1:8000/"

get_response = requests.post(endpoint, json={"title": "hey there is title", "content": 'hello world'}) #http request

# print(get_response.text)
# print(get_response.status_code)
print(get_response.json())