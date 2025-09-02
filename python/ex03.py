list = ["ieyasu", "ietada", "iemitsu", "ietsuna"]

for name in list:
    print(f"{name}様　晩餐会ご招待状")

absence = list.pop()
list.append("tsunayoshi")

print(f"{absence}様は不参加となりました")
for name in list:
    print(f"{name}様　晩餐会ご招待状")

list.insert(0, "ienobu")
list.insert(0, "ietsugu")
list.append("yoshimune")
for name in list:
    print(f"{name}様　晩餐会ご招待状")

while len(list)>2:
    cancel = list.pop()
    print(f"{cancel}様のお席がご用意できませんでした。")

for name in list:
    print(f"{name}様のお越しをお待ちしております。")

del list[0]
del list[0]

print(list)