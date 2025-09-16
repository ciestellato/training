import sqlite3
import numpy as np
import pandas as pd

df = pd.DataFrame({'a': np.arange(5),
                   'b': np.arange(5) + 1,
                   'c': np.arange(5) + 2})
print("元のデータフレーム:")
print(df)

conn = sqlite3.connect(':memory:')
cur = conn.cursor()

df.to_sql('sample', conn, if_exists='replace')

cur.execute('SELECT * FROM sample')
print("\nSQLから取得したデータ（fetchall）:")
print(cur.fetchall())

df2 = pd.read_sql('SELECT * FROM sample', conn).set_index('index')
print("\nSQLから読み込んだデータフレーム:")
print(df2)

cur.close()
conn.close()