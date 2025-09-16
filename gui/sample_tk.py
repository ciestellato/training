import tkinter as tk  # Tkinterの基本モジュールをインポート

window = tk.Tk()  # メインウィンドウを作成
window.title("tk 動作テスト")  # ウィンドウタイトルを設定

# ラベル（クラシックな見た目）
'''Labelコンストラクタを呼び出し、変数に代入する'''
label = tk.Label(window, text="こんにちは、tk！", font=("Arial", 12))
label.pack(pady=10) # 配置する　pady...上下の間隔。pady=20,10 だと上20,下20になる

# ボタン（クラシックな見た目）
button = tk.Button(window, text="クリック")
button.pack(pady=10)

# テキストボックス（Entry）
entry = tk.Entry(window)
entry.pack(pady=10)

window.mainloop()  # イベントループ開始