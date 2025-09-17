import requests
import zipfile
import io
import os
from dotenv import load_dotenv

# EDINETのAPIキー設定
load_dotenv()
api_key = os.getenv("EDINET_API_KEY")

# v2 APIのエンドポイント
url = "https://disclosure.edinet-fsa.go.jp/api/v2/documents.json"

# 取得対象の日付（例：2025年9月15日）
params = {
    "date": "2025-09-15",
    "type": 2,  # 書類一覧（1: 書類本体, 2: 書類一覧, 3: メタデータ）
    "Subscription-Key": api_key  # v2ではこのキー名が必要
}

# APIリクエスト
headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, params=params, headers=headers)

# 結果の確認
if response.status_code == 200:
    data = response.json()
    for doc in data["results"]:
        print(f"提出者: {doc['filerName']}, 書類種別: {doc['docTypeCode']}, EDINETコード: {doc['edinetCode']}")
else:
    print("取得に失敗しました。ステータスコード:", response.status_code)