import requests
import os
from dotenv import load_dotenv
from datetime import date

load_dotenv()
api_key = os.getenv("EDINET_API_KEY")
# print("APIキー:", api_key)  # ← ここで確認

# v2 APIのエンドポイント
url = "https://disclosure.edinet-fsa.go.jp/api/v2/documents.json"

params = {
    "date": date.today().strftime("%Y-%m-%d"),
    "type": 2,
    "Subscription-Key": api_key  # v2ではこのキー名が必要
}
headers = {
    "User-Agent": "Mozilla/5.0",
    "X-API-KEY": api_key
}

response = requests.get(url, params=params, headers=headers)
print("ステータスコード:", response.status_code)
print("レスポンスヘッダー:", response.headers)
print("レスポンス本文:", response.text)