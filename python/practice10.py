"""
📝 演習問題（ファイル名：practice10.py）
ユーザーに数値を入力させ、入力された数値をすべて合計するプログラムを作成してください。
ただし、q が入力されたらループを終了し、最終的な合計値を表示してください。

🔸ヒント：int() で数値変換、try-except で例外処理を加えるとより安全です。
"""

total = 0
keeping = True
prompt = "\n数値を入力してください(q:終了)\n"
while True:
    num = input(prompt)

    if num == "q":
        print(f"入力値の合計は、{total}です")
        break
    else:
        try:
            total += int(num)
        except ValueError:
            print(f"整数値を入力してください")