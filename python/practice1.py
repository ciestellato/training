"""
📝 演習問題（ファイル名：practice1.py）

変数 temperature に気温（整数）が入っているとき、
30度以上なら「暑い」、20〜29度なら「快適」、
それ未満なら「寒い」と表示するコードを書いてください。
"""

def how_about_temperature(temperature):
    if temperature >= 30:
        print(f"暑い")
    elif temperature >= 20:
        print(f"快適")
    else:
        print(f"寒い")

how_about_temperature(50)
how_about_temperature(30)
how_about_temperature(29.9)
how_about_temperature(20)
how_about_temperature(10)