"""
📝 演習問題（ファイル名：practice2.py）
変数 is_member = True と points = 120 があるとき、
会員でポイントが100以上なら「特典あり」、
それ以外は「特典なし」と表示するコードを書いてください。
"""

def check_benefit(is_member, points):
    if is_member and points >= 100:
        print(f"特典あり")
    else:
        print(f"特典なし")

check_benefit(True, 120)
check_benefit(True, 100)
check_benefit(True, 99)
check_benefit(False, 120)
check_benefit(False, 100)
check_benefit(False, 99)