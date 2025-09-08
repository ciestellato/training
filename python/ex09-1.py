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

if __name__ == "__main__":
    resto = Restaurant("来夢来人", "小料理屋")
    resto.describe_restaurant()
    resto.open_restaurant()