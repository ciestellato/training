import sqlite3
conn = sqlite3.connect(":memory:")

# カーソルを作成
cur = conn.cursor()

# テーブルを作成
cur.execute('CREATE TABLE hoge(id INTEGER PRIMARY KEY AUTOINCREMENT, name STRING, age INTEGER)')

# データを追加
cur.execute('INSERT INTO hoge(name, age) values("Taro", 12)')
cur.execute('INSERT INTO hoge(name) values("Hanako")')
cur.execute('INSERT INTO hoge(id, name, age) values(20, "Akiko", 2)')
cur.execute('INSERT INTO hoge(name, age) values("Jiro", 10)')

# 変更を確定
conn.commit()

cur.execute('SELECT * FROM hoge')  # hogeという名前のtableからすべて読んでくる
print(cur.fetchall())  # 上記で指定した範囲のrecordを取得する

cur.close()
conn.close()