import requests
import json

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

    # JSON構造を確認したい場合はここで一度だけ表示
    print(json.dumps(data, indent=2, ensure_ascii=False))

    # 正しいキー名に合わせてループ（例：case_studies）
    for i, case in enumerate(data.get("case_studies", []), start=1):
        print(f"{i}. {case.get('title', 'タイトルなし')}")
else:
    print("取得に失敗しました。ステータスコード:", response.status_code)