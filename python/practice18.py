"""
📝 演習問題（ファイル名：practice18.py）
Club クラスを定義し、インスタンスメソッドで名前を紹介し、クラスメソッドで全員の名前一覧を表示してください。
3人のメンバーを作成して確認してください。
"""

class Club:
    members = []

    def __init__(self, name):
        self.name = name
        print(f"こんにちは、{name}です")
        Club.members.append(self.name)
    
    @classmethod
    def print_all_members(cls):
        for member in Club.members:
            print(f"{member}")

if __name__ == "__main__":
    Club("amy")
    Club("bee")
    Club("chou")
    Club.print_all_members()