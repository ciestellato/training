from random import randint

class Die:
    """さいころクラス"""

    def __init__(self, sides=6):
        self.sides = sides
    
    def roll_die(self):
        num = randint(1, self.sides)
        print(f"{num}が出ました")
    
    def set_sides(self, sides):
        self.sides = sides

if __name__ == "__main__":
    d = Die()
    for i in range(1, 21):
        print(f"{i}回目:", end="")
        d.roll_die()
    print("----------------------")
    
    d.set_sides(10)
    for i in range(1, 21):
        print(f"{i}回目:", end="")
        d.roll_die()
    print("----------------------")

    d20 = Die(20)
    for i in range(1, 21):
        print(f"{i}回目:", end="")
        d20.roll_die()
    print("----------------------")