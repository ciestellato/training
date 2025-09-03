print([num for num in range(1,21)])

list = range(1, 1000001)
print(min(list))
print(max(list))
print(sum(list))

list = range(1, 21, 2)
print([num for num in list])

list = range(3, 301, 3)
print([num for num in list])

cubes = [num**3  for num in range(1, 11)]
for cube in cubes:
    print(cube)

print("リストの最初の3つの要素です")
print(list[:4])
print("リストの中央の3つの要素です")
print(list[1:4])
print("リストの最後の3つの要素です")
print(list[-3:])