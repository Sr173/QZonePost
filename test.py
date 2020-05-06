import requests

requests.post("http://localhost:886/v1/store", json={
    "key": "123",
    "value": "456"
})