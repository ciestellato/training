colors = ('green', 'yellow', 'red')
alien_color = colors[0]

if alien_color == 'green':
    print("おめでとうございます！5点獲得です")

alien_color = colors[2]
if alien_color == 'green':
    print("おめでとうございます！5点獲得です")
elif alien_color == 'red':
    print("おめでとうございます！15点獲得です")
else:
    print("おめでとうございます！10点獲得です")

age = 10

if age < 2:
    print("hello, baby!")
elif age < 4:
    print("you are toddler")
elif age < 13:
    print("just kid")
elif age < 20:
    print("teen ager")
elif age < 65:
    print("you are adult")
else:
    print("senior")

favorite_fruits = ["apple", "strawberry", "banana"]
target = "banana"
if target in favorite_fruits:
    print(f"you like {target}, right?")



def searchFruit(target):
    if target in favorite_fruits:
        print(f"you like {target}, right?")


searchFruit("orange")
searchFruit("apple")