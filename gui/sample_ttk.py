import tkinter as tk  # Tkinterの基本モジュールをインポート
from tkinter import ttk  # ttkモジュールをインポート（テーマ付き）

window = tk.Tk()  # メインウィンドウを作成
window.title("ttk ウィジェット")  # ウィンドウタイトルを設定

# ラベル（モダンな見た目）
label = ttk.Label(window, text="こんにちは、ttk！")
label.pack(pady=10)

# ボタン（モダンな見た目）
button = ttk.Button(window, text="クリック")
button.pack(pady=10)

# テキストボックス（Entry）
entry = ttk.Entry(window)
entry.pack(pady=10)

# コンボボックス（ドロップダウン選択）
combobox = ttk.Combobox(window, values=["東京", "大阪", "名古屋", "博多"])
combobox.current(0)  # 初期選択
combobox.pack(pady=10)

window.mainloop()  # イベントループ開始