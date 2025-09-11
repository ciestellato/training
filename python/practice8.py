"""
📝 演習問題（ファイル名：practice8.py）
リスト colors = ["赤", "青", "緑"] に「黄」を追加し、「青」を削除して、昇順に並び替えた結果を表示するコードを書いてください。
"""

colors = ["赤", "青", "緑"]
colors.append("黄")
colors.remove("青")
colors.sort()
print(f"{colors}")

"""
✅ サンプルコード●
# フルーツのリストを定義
fruits = ["りんご", "バナナ", "みかん"]

# 要素の追加
fruits.append("ぶどう")  # 末尾に追加

# 要素の挿入（インデックス指定）
fruits.insert(1, "キウイ")  # インデックス1に挿入

# 要素の削除
fruits.remove("バナナ")  # 最初に見つかった"バナナ"を削除

# ソート（昇順）
fruits.sort()

# 結果表示
print("現在のフルーツ一覧:", fruits)

💡 ポイント解説
.append()：末尾に追加
.insert(index, value)：指定位置に挿入
.remove(value)：最初に一致した要素を削除
.sort()：昇順に並び替え（文字列なら辞書順）
リストは可変で、状態変化を伴う処理に強い
"""