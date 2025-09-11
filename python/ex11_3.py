class Employee:
    """従業員クラス"""

    def __init__(self, name, family_name, salary):
        self.name = name
        self.family_name = family_name
        self.salary = salary
    
    def give_raise(self, increase=500000):
        self.salary += increase