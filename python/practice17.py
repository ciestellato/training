"""
📝 演習問題（ファイル名：practice17.py）
Student クラスを定義し、インスタンスごとに名前を保持し、
クラス変数で学生数をカウントしてください。2人の学生を作成し、名前と人数を表示してください。
"""

class Student:
    """生徒クラス"""
    count = 0

    def __init__(self, name):
        self.name = name
        Student.count += 1
    
    @classmethod
    def show_count(cls):  # クラスメソッドには cls を使う
        print("現在のメンバー数:", cls.count)

if __name__ == "__main__":
    s1 = Student("若林")
    s2 = Student("岬")
    print(Student.count)
    Student.show_count()

"""
💡 ポイント解説
- クラス変数はすべてのインスタンスで共有される。
- クラスメソッドは @classmethod を使い、cls を引数に取る。
- クラスメソッドはクラス名から直接呼び出す。"""