"""
📝 演習問題（ファイル名：practice16.py）
名前と職業を保持するクラス Employee を定義し、
インスタンスを作成して「○○さんの職業は△△です」と表示するメソッドを作成してください。
"""

class Emloyee:
    """従業員クラス"""
    def __init__(self, name, job):
        self.name = name
        self.job = job
    
    def print_info(self):
        print(f"{self.name}さんの職業は{self.job}です")

if __name__ == "__main__":
    e = Emloyee("ぽこ", "エグゼクティブプロデューサー")
    e.print_info()