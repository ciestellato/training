import requests
from datetime import date
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("EDINET_API_KEY")

url = "https://disclosure.edinet-fsa.go.jp/api/v1/documents.json"
params = {
    "date": date.today().strftime("%Y-%m-%d"),
    "type": 2
}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "X-API-KEY": api_key
}

response = requests.get(url, params=params, headers=headers)
print("ステータスコード:", response.status_code)