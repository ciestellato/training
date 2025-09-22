# WinでもUnicodeDecodeErrorになった

```
import pandas as pd

filename = r"C:\Users\0602JP\Desktop\XBRL_TO_CSV\jpaud-qrr-cc-001_E05494-000_2025-06-30_01_2025-08-06.csv"

df = pd.read_csv(filename, index_col=0, encoding='utf-8')
print(df)
```

## 参考サイト

- []

## やったこと

### ファイルのエンコーディングを確認する

```
with open(filename, "rb") as file:
    raw_data = file.read()
result = chardet.detect(raw_data)
print(result["encoding"]) # 推定されるエンコーディングを表示
```

> UTF-16