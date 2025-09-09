filename = 'guest.txt'
prompt = "お名前を入力してください"
prompt += "\n終了する場合は「end」と入力してください\n"
keep = True

with open(filename, 'a', encoding="UTF-8") as file_object:
    while keep:
        name = input(prompt)
        if name == "end":
            keep = False
        else:
            file_object.write(f"{name}\n")

