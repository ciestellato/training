"""
📝 演習問題（ファイル名：practice14.py）
任意の数の文字列を受け取り、それらをすべて1行で表示する関数を定義してください。
関数を呼び出して、"Python", "is", "fun" を渡して表示してください。（ヒント：join()関数を調べると処理が簡単になります）
"""

def print_words(*words):
    result = "_".join(words)
    print(result)

print_words("Python", "is", "fun" )

