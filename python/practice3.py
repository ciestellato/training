"""
📝 演習問題（ファイル名：practice3.py）
リスト scores = [72, 88, 95, 60, 79] の中から、
80点以上のスコアだけを「合格」として表示するコードを書いてください。
"""

def check_passed(point):
    if point >= 80:
        print(f"合格: {point}点")
    else:
        print(f"不合格")

if __name__ == "__main__":
    scores = [72, 88, 95, 60, 79]
    for score in scores:
        check_passed(score)