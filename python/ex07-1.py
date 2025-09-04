prompt = "どんな車種をご希望ですか？"
car = input(prompt)
print(f"{car}の手配を試みます")

prompt = "ディナーに何人参加しますか？"
num = int(input(prompt))
if num > 8:
    print("お席のご用意にお時間を要する可能性があります。")
else:
    print("お席へご案内いたします。")

prompt = "数字を入力してください"
num = int(input(prompt))
if num % 10 == 0:
    print("10の倍数です！")
else:
    print("10の倍数ではありません！")