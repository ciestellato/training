def make_pizza(size, *toppings):
    """注文されたピザの要約を出力する"""
    print(f"\n{size}インチのピザを、以下のトッピングで作ります。")
    for topping in toppings:
        print(f"- {topping}")

if __name__ == "__main__":
    make_pizza(12) # 第2引数は0～N個
    make_pizza(12, "ハム", "チーズ")