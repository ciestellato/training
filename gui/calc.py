import tkinter as tk  # Tkinterの基本GUIモジュールをインポート
from tkinter import ttk  # ttkモジュール（スタイル付きウィジェット）をインポート

def make_number():
    """ユーザーが選択した計算方法で計算して値を返す"""
    # Listboxの選択状態を取得
    selection = calc_listbox.curselection()
    
    if not selection:
        result_label.config(text="計算方法を選択してください。")
        return
    
    how_to_calc = calc_listbox.get(selection[0])
    val1 = int(num1.get())
    val2 = int(num2.get())
    if how_to_calc == "+":
        result = val1 + val2
    elif how_to_calc == "-":
        result = val1 - val2
    elif how_to_calc == "x":
        result = val1 * val2
    else:
        result = val1 / val2

    result_label.config(text=f"{val1} {how_to_calc} {val2} = {result}")

# メインウィンドウを作成
window = tk.Tk()

# ウィンドウのタイトルを設定
window.title("計算フォーム")

# 数値1のラベルを作成し、左寄せで配置
tk.Label(window, text="数値1:").pack(anchor="w", padx=10)
num1 = tk.Entry(window)
num1.pack(padx=10)

# 数値2のラベルを作成し、左寄せで配置
tk.Label(window, text="数値2:").pack(anchor="w", padx=10)
num2 = tk.Entry(window)
num2.pack(padx=10)

# 計算式選択用のラベルを作成し、左寄せで配置
tk.Label(window, text="計算方法を選択:").pack(anchor="w", padx=10)

# Listboxウィジェットを作成（高さ4行分）
calc_listbox = tk.Listbox(window, height=4)

# 計算式の選択肢をListboxに追加
for item in ["+", "-", "x", "/"]:
    calc_listbox.insert(tk.END, item)

# Listboxをウィンドウに配置
calc_listbox.pack(padx=10)

# 計算ボタンを作成し、押下時に make_number 関数を呼び出す
ttk.Button(window, text="計算する", command=make_number).pack(pady=10)

# 結果表示用のラベルを作成（背景色を黄色に設定）
result_label = tk.Label(window, text="", bg="lightyellow")

# 結果表示ラベルをウィンドウに配置
result_label.pack(padx=10, pady=10)

# イベントループを開始（ウィンドウを表示し、操作を待機）
window.mainloop()
