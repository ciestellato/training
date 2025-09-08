class Restaurant:
    """レストランをモデル化"""

    def __init__(self, name, type):
        self.restaurant_name = name
        self.cuisine_type = type
        self.number_served = 0
    
    def describe_restaurant(self):
        print(f"レストラン名: {self.restaurant_name}")
        print(f"種類: {self.cuisine_type}")
    
    def open_restaurant(self):
        print(f"新たに{self.cuisine_type}「{self.restaurant_name}」がオープンしました")
    
    def set_number_served(self, num):
        self.number_served = num
    
    def increment_number_served(self, num):
        self.number_served += num

class IceCreamStand(Restaurant):
    """レストランを継承したアイスクリームスタンドのクラス"""

    def __init__(self, name, type):
        super().__init__(name, type)
        self.fravors = []

    def print_flavors(self):
        for f in self.fravors:
            print(f, sep=" , ")
    
    def add_flavor(self, flavor):
        self.fravors.append(flavor)

if __name__ == "__main__":
    ice = IceCreamStand("Ben & Jerry", "アイスクリーム")
    ice.fravors.append("ロッキーロード")
    ice.fravors.append("ナポリタン")
    ice.fravors.append("ミルキーウェイ")
    ice.add_flavor("ドルチェピカンテ")
    ice.print_flavors()
