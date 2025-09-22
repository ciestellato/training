import pandas as pd
import chardet

filename = r"C:\Users\0602JP\Desktop\XBRL_TO_CSV\jpaud-qrr-cc-001_E05494-000_2025-06-30_01_2025-08-06.csv"

df = pd.read_csv(filename, index_col=0, encoding='utf-16')
print(df)

"""
with open(filename, "rb") as file:
    raw_data = file.read()
result = chardet.detect(raw_data)
print(result["encoding"]) # 推定されるエンコーディングを表示
"""