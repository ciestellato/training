import sqlite3
conn = sqlite3.connect('./TEST.db')

cur = conn.cursor()  # カーソルを作成
# cur.execute('CREATE TABLE persons(id INTEGER PRIMARY KEY AUTOINCREMENT, name STRING)')  # tableを作成する指示
# 存在しない時のみテーブル作成
cur.execute('CREATE TABLE IF NOT EXISTS persons(id INTEGER PRIMARY KEY AUTOINCREMENT, name STRING)')

cur.execute("SELECT name from sqlite_master where type='table';")
print('table一覧: ', cur.fetchall())

conn.commit()  # commit()した時点でDBファイルが更新されます
conn.close()
