import requests
import zipfile
import io
import os
from dotenv import load_dotenv

# EDINET APIのエンドポイント
url = "https://disclosure.edinet-fsa.go.jp/api/v1/documents.json"

# 取得対象の日付（例：2025年9月15日）
params = {
    "date": "2025-09-15",
    "type": 2  # 書類一覧（1: 書類本体, 2: 書類一覧, 3: メタデータ）
}

# EDINETのAPIキー設定
load_dotenv()
api_key = os.getenv("EDINET_API_KEY")

# APIリクエスト
headers = {
    "User-Agent": "Mozilla/5.0",
    "X-API-KEY": api_key

}
response = requests.get(url, params=params, headers=headers)

# 結果の確認
if response.status_code == 200:
    data = response.json()
    for doc in data["results"]:
        print(f"提出者: {doc['filerName']}, 書類種別: {doc['docTypeCode']}, EDINETコード: {doc['edinetCode']}")
else:
    print("取得に失敗しました。ステータスコード:", response.status_code)