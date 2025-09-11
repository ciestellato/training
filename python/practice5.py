"""
📝 演習問題（ファイル名：practice5.py）
リスト scores = [65, 80, 90, 75] の各要素に5点加点し、
新しいリストとして表示するコードを書いてください。
"""

scores = [65, 80, 90, 75]
added_scores = []
for score in scores:
    num = score + 5
    added_scores.append(num)

print(f"added_score:{added_scores}")