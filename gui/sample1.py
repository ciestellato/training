import tkinter as tk  # Tkinterモジュールをインポート
from tkinter import ttk  # ttkモジュール（スタイル付きウィジェット）をインポート

def show_name():
    # Entryから氏と名を取得して連結
    full_name = f"{last_entry.get()} {first_entry.get()}"
    result_label.config(text=f"氏名: {full_name}")  # ラベルに表示

window = tk.Tk()  # メインウィンドウを作成
window.title("氏名入力フォーム")  # ウィンドウタイトルを設定

tk.Label(window, text="氏:").pack(anchor="w", padx=10)  # 氏ラベル
last_entry = tk.Entry(window)  # 氏入力欄
last_entry.pack(padx=10)

tk.Label(window, text="名:").pack(anchor="w", padx=10)  # 名ラベル
first_entry = tk.Entry(window)  # 名入力欄
first_entry.pack(padx=10)

ttk.Button(window, text="表示", command=show_name).pack(pady=10)  # 表示ボタン

result_label = tk.Label(window, text="", bg="lightyellow", width=40)  # 結果表示ラベル
result_label.pack(padx=10, pady=10)

window.mainloop()  # イベントループ開始