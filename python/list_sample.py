car_makers = ["honda", "toyota", "mitsubishi"]
print(car_makers[-1])

car_makers.append("daihatsu")
car_makers.insert(2, "nissan")

for car in car_makers:
    print(car)