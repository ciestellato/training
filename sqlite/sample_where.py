import sqlite3
conn = sqlite3.connect(":memory:")

# カーソルの作成
cur = conn.cursor()

# テーブルの作成
cur.execute('CREATE TABLE hoge(id INTEGER PRIMARY KEY AUTOINCREMENT, name STRING, age INTEGER)')

# データの挿入
cur.execute('INSERT INTO hoge(name, age) values("Taro", 12)')
cur.execute('INSERT INTO hoge(name) values("Hanako")')
cur.execute('INSERT INTO hoge(id, name, age) values(20, "Akiko", 2)')
cur.execute('INSERT INTO hoge(name, age) values("Jiro", 10)')

# 変更を確定
conn.commit()

# SELECT文を実行してデータを取得、表示
cur.execute('SELECT * FROM hoge WHERE age <= 12')
print(cur.fetchall())

cur.execute('SELECT * FROM hoge WHERE name = "Hanako"')
print(cur.fetchall())

cur.execute('SELECT * FROM hoge WHERE name <> "Jiro"')
print(cur.fetchall())

cur.close()
conn.close()
