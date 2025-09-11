"""
📝 演習問題（ファイル名：practice4.py）
変数 energy = 10 を使って、1回ごとに energy を2ずつ減らしながら
「行動しました」と表示し、energy が0未満になったら終了するコードを書いてください。
"""

energy = 10
for i in range(energy, 0, -2):
    print(f"行動しました。エネルギー残量：{i}")