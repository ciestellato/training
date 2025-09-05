# 8-3
def make_shirt(size, msg):
    print(f"{size}サイズで「{msg}」と印字したTシャツを作成します")

make_shirt("XL", "LOVE BREAD")
make_shirt(msg="お犬様", size="S")

# 8-4
def make_shirt(size="L", msg="I love Python"):
    print(f"{size}サイズで「{msg}」と印字したTシャツを作成します")

make_shirt()
make_shirt("M")
make_shirt("XL", "LOVE BREAD")

# 8-5
def describe_city(city, country="イタリア"):
    print(f"{city}は{country}にあります。")

describe_city("ネアポリス")
describe_city("鹿児島", "日本")
describe_city("ウィーン", "オーストリア")