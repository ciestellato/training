class Book:
    """"本のクラス"""

    def __init__(self, title, author, price):
        self.title = title
        self.author = author
        self.price = price
    
    def show(self):
        print(f"{self.author}著「{self.title}」{self.price}円")


if __name__ == "__main__":
    b1 = Book("わがねこ", "夏目漱石", 880)
    b1.show()