import requests

headers = {
    "x-token": "my_secure_token"
}
response = requests.get("http://127.0.0.1:8000/scrape?pages=2", headers=headers)
print(response.json())
