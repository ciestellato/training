import tkinter as tk  # Tkinterの基本GUIモジュールをインポート
from tkinter import ttk  # ttkモジュール（スタイル付きウィジェット）をインポート

# ボタン押下時に注文内容を取得してラベルに表示する関数
def show_order():
    # Listboxの選択状態を取得
    selection = pizza_listbox.curselection()
    
    if not selection:
        result_label.config(text="ピザを選択してください。")
        return
    
    pizza = pizza_listbox.get(selection[0])
    quantity = quantity_combo.get()
    result_label.config(text=f"注文: {pizza} × {quantity}個")

# メインウィンドウを作成
window = tk.Tk()

# ウィンドウのタイトルを設定
window.title("ピザ注文フォーム")

# ピザ選択用のラベルを作成し、左寄せで配置
tk.Label(window, text="ピザを選択:").pack(anchor="w", padx=10)

# Listboxウィジェットを作成（高さ4行分）
pizza_listbox = tk.Listbox(window, height=4)

# ピザの選択肢をListboxに追加
for item in ["マルゲリータ", "ペパロニ", "シーフード", "ベジタブル"]:
    pizza_listbox.insert(tk.END, item)

# Listboxをウィンドウに配置
pizza_listbox.pack(padx=10)

# 数量選択用のラベルを作成し、左寄せで配置
tk.Label(window, text="数量を選択:").pack(anchor="w", padx=10)

# Comboboxウィジェットを作成（選択肢は1〜5、選択のみ可能な状態）
quantity_combo = ttk.Combobox(window, values=[str(i) for i in range(1, 6)], state="readonly")

# 初期選択を「1個」に設定
quantity_combo.current(0)

# Comboboxをウィンドウに配置
quantity_combo.pack(padx=10)

# 注文ボタンを作成し、押下時に show_order 関数を呼び出す
ttk.Button(window, text="注文する", command=show_order).pack(pady=10)

# 結果表示用のラベルを作成（背景色を黄色に設定）
result_label = tk.Label(window, text="", bg="lightyellow")

# 結果表示ラベルをウィンドウに配置
result_label.pack(padx=10, pady=10)

# イベントループを開始（ウィンドウを表示し、操作を待機）
window.mainloop()
