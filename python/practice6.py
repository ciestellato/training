"""
📝 演習問題（ファイル名：practice6.py）
タプル book = ("Python入門", "山田太郎", 2022) を使って、
「書名：〜、著者：〜、出版年：〜」という形式で表示するコードを書いてください。
"""

book = ("Python入門", "山田太郎", 2022)
title = book[0]
author = book[1]
published = book[2]

print(f"書名：{title} 著者：{author} 出版年：{published}")

"""
💡 ポイント解説
- タプルは「変更不可」なリストのようなもの。
- 要素の順序や意味が固定されているデータに向いている。
- インデックスでアクセス可能だが、.append() や .remove() は使えない。
- アンパック（name, age, city = user）も可能。
"""