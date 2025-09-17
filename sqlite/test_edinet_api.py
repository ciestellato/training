import requests
from datetime import date
import os
from dotenv import load_dotenv

# .envファイルからAPIキーを読み込む
load_dotenv()
api_key = os.getenv("EDINET_API_KEY")

# v2 APIのエンドポイント
url = "https://disclosure.edinet-fsa.go.jp/api/v2/documents.json"

# パラメータの設定（今日の日付を使用）
params = {
    "date": date.today().strftime("%Y-%m-%d"),
    "type": 2,
    "Subscription-Key": api_key  # v2ではこのキー名が必要
}

# ヘッダーは必須ではないが、User-Agentを指定しておくと安定する場合あり
headers = {
    "User-Agent": "Mozilla/5.0"
}

# APIリクエストを送信
response = requests.get(url, params=params, headers=headers)

# ステータスコードとレスポンス内容を表示
print("ステータスコード:", response.status_code)
try:
    print("レスポンス:", response.json())
except Exception as e:
    print("JSONの解析に失敗しました:", e)