import requests
import pandas as pd

url = "https://mirasapo-plus.go.jp/jirei-api/case_studies"
params = {
    "keywords": "デジタル化,生産性向上",
    "limit": 5
}
headers = {
    "Accept": "application/json"
}

response = requests.get(url, params=params, headers=headers)

if response.status_code == 200:
    data = response.json()
    case_list = data.get("items", [])  # ← 正しいキーに変更！

    df = pd.DataFrame([
        {
            "タイトル": case.get("title"),
            "業種": case.get("organization", {}).get("industry"),
            "地域": case.get("location", {}).get("name"),
            "概要": case.get("summary"),
            "企業名": case.get("organization", {}).get("name"),
            "発表年": case.get("year")
        }
        for case in case_list
    ])

    pd.set_option("display.max_colwidth", None)
    print(df)

    # CSVに保存
    df.to_csv("事例一覧.csv", index=False, encoding="utf-8-sig")
else:
    print("取得に失敗しました。ステータスコード:", response.status_code)