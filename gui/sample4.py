import tkinter as tk  # Tkinterの基本GUIモジュールをインポート
from tkinter import ttk  # ttkモジュール（スタイル付きウィジェット）をインポート

# ボタン押下時に選択された趣味を取得してラベルに表示する関数
def show_hobbies():
    # Listboxから選択されたインデックスを取得し、対応する文字列をリストに格納
    selected = [hobby_listbox.get(i) for i in hobby_listbox.curselection()]
    
    # 選択された趣味をカンマ区切りで整形してラベルに表示
    result_label.config(text=f"趣味: {', '.join(selected)}")

# メインウィンドウを作成
window = tk.Tk()

# ウィンドウのタイトルを設定
window.title("趣味選択フォーム")

# 趣味選択用のラベルを作成し、左寄せで配置
tk.Label(window, text="趣味を選択（複数可）:").pack(anchor="w", padx=10)

# Listboxウィジェットを作成（複数選択モード、表示高さ6行）
hobby_listbox = tk.Listbox(window, selectmode="multiple", height=6)

# 趣味の選択肢をListboxに追加
for hobby in ["読書", "映画鑑賞", "旅行", "料理", "ゲーム", "音楽"]:
    hobby_listbox.insert(tk.END, hobby)

# Listboxをウィンドウに配置
hobby_listbox.pack(padx=10)

# 表示ボタンを作成し、押下時に show_hobbies 関数を呼び出す
ttk.Button(window, text="表示", command=show_hobbies).pack(pady=10)

# 結果表示用のラベルを作成（背景色と文字配置を指定）
result_label = tk.Label(window, text="", bg="lightyellow", justify="left")

# 結果表示ラベルをウィンドウに配置（領域を広げて表示）
result_label.pack(fill="both", expand=True, padx=10, pady=10)

# イベントループを開始（ウィンドウを表示し、操作を待機）
window.mainloop()