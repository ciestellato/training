"""
📝 演習問題（ファイル名：practice13.py）
リストで渡された複数の名前を1人ずつ表示する関数を定義してください。
関数を呼び出して、["鈴木", "田中", "佐藤"] を渡して表示してください。"""

def print_names(names):
    for name in names:
        print(name)

names = ["鈴木", "田中", "佐藤"]
print_names(names)