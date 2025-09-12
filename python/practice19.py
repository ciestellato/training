"""
📝 演習問題（ファイル名：practice19.py）
Animal クラスを定義し、Dog クラスがそれを継承するようにしてください。
Dog クラスには犬種を追加し、「○○は△△という犬種です」と表示するメソッドを作成してください。
"""

class Animal:

    def __init__(self, name):
        self.name = name

class Dog(Animal):

    def __init__(self, name, type):
        super().__init__(name)
        self.type = type
    
    def print_info(self):
        print(f"{self.name}は、{self.type}という犬種です")

if __name__ == "__main__":
    maru = Dog("maru", "柴犬")
    maru.print_info()