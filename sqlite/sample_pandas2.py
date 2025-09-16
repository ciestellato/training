import requests
import pandas as pd
import json

url = "https://mirasapo-plus.go.jp/jirei-api/case_studies"
params = {
    "keywords": "デジタル化,生産性向上",
    "limit": 1
}
headers = {
    "Accept": "application/json"
}

response = requests.get(url, params=params, headers=headers)

if response.status_code == 200:
    data = response.json()
    print(json.dumps(data, indent=2, ensure_ascii=False))  # ← 構造確認

    # キー名を確認してからここを調整
    case_list = data.get("results", [])  # ← ここを正しいキーに変更

    df = pd.DataFrame([
        {
            "タイトル": case.get("title"),
            "業種": case.get("industry"),
            "地域": case.get("region"),
            "概要": case.get("summary")
        }
        for case in case_list
    ])

    pd.set_option("display.max_colwidth", None)
    print(df)
else:
    print("取得に失敗しました。ステータスコード:", response.status_code)