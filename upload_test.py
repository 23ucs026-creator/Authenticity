import requests

# INSERT YOUR NEW TOKEN HERE
jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2ODIxMjgxNSwianRpIjoiZmY4MDI5YmMtZWQ2My00OWY0LWEyMmQtYTZlYTNhOGUyMWU4IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjEiLCJuYmYiOjE3NjgyMTI4MTUsImNzcmYiOiI2ZDM0ZjgwNy1kZTc2LTRjNTAtYjVkZC02ZDhmZDExMDQ4N2UiLCJleHAiOjE3NjgyMTM3MTV9.z5uhRvEJvy9cQNSBhkpnjVws4AG9T_vqrM7bbp552aM"

url = "http://127.0.0.1:5000/documents/upload"

headers = {
    "Authorization": f"Bearer {jwt_token}"
}

files = {
    "file": open(r"U:\csta26\Authenticity\dummy.pdf", "rb")
}

response = requests.post(url, headers=headers, files=files)

print("--- Upload Response ---")
print("Status Code:", response.status_code)
print(response.text)
