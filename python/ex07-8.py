sandwich_orders = ["ハムレタス", "BLT", "たまごサンド", "フルーツサンド"]
finished_sandwiches = []
while sandwich_orders:
    done = sandwich_orders.pop()
    print(f"{done}ができました")
    finished_sandwiches.append(done)
print("すべてのサンドイッチが完成しました")

responses = {}
# 投票がアクティブなことを示すフラグ
polling_active = True

while polling_active:
    prompt = "世界中どこでも行けるとしたらどこに行きたいですか？"
    place = input(prompt)
    num = responses.get(place)
    if num:
        responses[place] = num + 1
    else:
        responses[place] = 1

    prompt = "投票を続けますか？ (y/n)"
    repeat = input(prompt)
    if repeat == "n":
        polling_active = False

# 投票を終了し、結果を表示する
print("\n --- 投票結果 ---")
for place, num in responses.items():
    print(f"{place} : {num}票")