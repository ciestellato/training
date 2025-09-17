import tkinter as tk  # Tkinterモジュールをインポート

window = tk.Tk()  # メインウィンドウを作成
window.title("グリッドレイアウトの例")  # ウィンドウタイトルを設定

# ラベル1を作成し、0行0列に配置
label1 = tk.Label(window, text="名前:")
label1.grid(row=0, column=0, padx=5, pady=5)

# Entry1を作成し、0行1列に配置
entry1 = tk.Entry(window)
entry1.grid(row=0, column=1, padx=5, pady=5)

# ラベル2を作成し、1行0列に配置
label2 = tk.Label(window, text="年齢:")
label2.grid(row=1, column=0, padx=5, pady=5)

# Entry2を作成し、1行1列に配置
entry2 = tk.Entry(window)
entry2.grid(row=1, column=1, padx=5, pady=5)

# ボタンを作成し、2行0列〜1列にまたがって配置
button = tk.Button(window, text="送信")
button.grid(row=2, column=0, columnspan=2, pady=10)

window.mainloop()  # イベントループ開始