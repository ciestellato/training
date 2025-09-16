import requests
import os
from dotenv import load_dotenv
from datetime import date

load_dotenv()
api_key = os.getenv("EDINET_API_KEY")
print("APIキー:", api_key)  # ← ここで確認

url = "https://disclosure.edinet-fsa.go.jp/api/v1/documents.json"
params = {
    "date": date.today().strftime("%Y-%m-%d"),
    "type": 2
}
headers = {
    "User-Agent": "Mozilla/5.0",
    "X-API-KEY": api_key
}

response = requests.get(url, params=params, headers=headers)
print("ステータスコード:", response.status_code)
print("レスポンスヘッダー:", response.headers)
print("レスポンス本文:", response.text)