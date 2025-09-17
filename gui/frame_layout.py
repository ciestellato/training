import tkinter as tk  # Tkinterモジュールをインポート

window = tk.Tk()  # メインウィンドウを作成
window.title("Frameレイアウトの例")  # ウィンドウタイトルを設定

# 名前入力用のFrameを作成（背景色を設定）
frame_name = tk.Frame(window, bg="lightblue", padx=10, pady=10)
frame_name.pack(fill="x", padx=10, pady=5)  # 横方向に広げて配置

# 年齢入力用のFrameを作成（背景色を設定）
frame_age = tk.Frame(window, bg="lightgreen", padx=10, pady=10)
frame_age.pack(fill="x", padx=10, pady=5)

# ボタン用のFrameを作成
frame_button = tk.Frame(window)
frame_button.pack(fill="x", padx=10, pady=10)

# 名前入力欄をFrame内に配置（左寄せ）
tk.Label(frame_name, text="名前:").pack(side="left", padx=5)
tk.Entry(frame_name).pack(side="left", padx=5)

# 年齢入力欄をFrame内に配置（左寄せ）
tk.Label(frame_age, text="年齢:").pack(side="left", padx=5)
tk.Entry(frame_age).pack(side="left", padx=5)

# 送信ボタンをFrame内に配置（中央寄せ）
tk.Button(frame_button, text="送信").pack()

window.mainloop()  # イベントループ開始
