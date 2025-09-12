"""
📝 演習問題（ファイル名：practice20.py）
Company クラスと Employee クラスを定義し、Company が Employee を保持する構造を作成してください。
会社名と社員名、社員の出身地を表示するメソッドを作成してください。"""

class Employee:

    def __init__(self, name, country):
        self.name = name
        self.country = country

class Company:

    def __init__(self, name):
        self.name = name
        self.employees = []
    
    def add_employee(self, employee):
        self.employees.append(employee)
    
    def print_info(self):
        print(f"会社名：{self.name}")
        for employee in self.employees:
            print(f"{employee.name}({employee.country}出身)")

if __name__ == "__main__":
    comp = Company("スプーキーズ")

    m1 = Employee("ランチ", "自動車工場")
    m2 = Employee("スプーキー", "モノリス")
    m3 = Employee("シックス", "屋敷")
    comp.add_employee(m1)
    comp.add_employee(m2)
    comp.add_employee(m3)
    comp.print_info()