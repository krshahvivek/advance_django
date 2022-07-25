import requests

endpoint = "http://localhost:8000/api/products/"

get_response = requests.get(endpoint, json={"title": "hey there is title", "content": 'hello world'})

# print(get_response.text)
# print(get_response.status_code)
print(get_response.json())