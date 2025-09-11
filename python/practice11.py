"""
📝 演習問題（ファイル名：practice11.py）
2つの文字列を受け取り、結合して表示する関数を定義してください。関数を呼び出して、
"Hello" と "World" を結合した結果を表示してください。
"""

def words_concater(word1, word2):
    return f"{word1}_{word2}"

word = words_concater("Hello", "World")
print(f"{word}")