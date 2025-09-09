from random import choice,randint

nums = []
for i in range(10):
    nums.append(randint(0, 100))

for i in range(4):
    hit = choice(nums)
    print(f"{hit}　が、当たりです！")