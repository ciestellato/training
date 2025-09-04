prompt = "何をトッピングしますか？"
prompt += "\n「以上」で終了します。"
more = True

while more:
    topping = input(prompt)
    if topping == "以上":
        print("終了します")
        more = False
        break
    print(f"{topping}を載せます")
    