import tkinter as tk  # Tkinterモジュールをインポート（GUI構築用）
from tkinter import ttk  # ttkモジュールをインポート（スタイル付きウィジェット用）

# ボタン押下時に入力内容を取得して表示する関数
def show_input():
    # Entryウィジェットから入力された名前を取得
    name = name_entry.get()

    # Textウィジェットから説明文を取得（1.0は1行目の先頭、tk.ENDは末尾）
    description = text_area.get("1.0", tk.END).strip()  # strip()で余分な改行を除去

    # Listboxウィジェットから選択されたインデックスを取得（複数選択対応）
    selected_indices = listbox.curselection()

    # インデックスから実際の果物名を取得してリストに格納
    selected_items = []
    for index in selected_indices:
        selected_items.append(listbox.get(index))

    # Comboboxウィジェットから選択された都市名を取得
    city = combobox.get()

    # 取得したすべての情報を整形してラベルに表示
    result = f"名前: {name}\n説明: {description}\n選択項目: {', '.join(selected_items)}\n都市: {city}"
    result_label.config(text=result)  # ラベルのテキストを更新

# メインウィンドウを作成
window = tk.Tk()
window.title("入力フォームサンプル")  # ウィンドウのタイトルを設定
window.geometry("400x500")  # ウィンドウサイズ（幅×高さ）を指定

# 名前入力用のラベルを作成し、左寄せで配置
name_label = tk.Label(window, text="名前:", font=("Arial", 12))
name_label.pack(anchor="w", padx=10, pady=5)

# Entryウィジェット（テキストボックス）を作成し、配置
name_entry = tk.Entry(window, width=30)
name_entry.pack(padx=10)

# 説明入力用のラベルを作成し、左寄せで配置
desc_label = tk.Label(window, text="説明:", font=("Arial", 12))
desc_label.pack(anchor="w", padx=10, pady=5)

# Textウィジェット（複数行テキストエリア）を作成し、配置
text_area = tk.Text(window, width=40, height=5)
text_area.pack(padx=10)

# 果物選択用のラベルを作成し、左寄せで配置
fruit_label = tk.Label(window, text="好きな果物を選んでください:", font=("Arial", 12))
fruit_label.pack(anchor="w", padx=10, pady=5)

# Listboxウィジェット（複数選択可能）を作成
listbox = tk.Listbox(window, selectmode="multiple", height=4)

# Listboxに果物の選択肢を追加
for fruit in ["りんご", "みかん", "バナナ", "ぶどう"]:
    listbox.insert(tk.END, fruit)

# Listboxを配置
listbox.pack(padx=10)

# 都市選択用のラベルを作成し、左寄せで配置
city_label = tk.Label(window, text="都市を選択:", font=("Arial", 12))
city_label.pack(anchor="w", padx=10, pady=5)

# Comboboxウィジェット（ドロップダウン）を作成（選択のみ可能な状態）
combobox = ttk.Combobox(window, state="readonly")

# Comboboxに都市の選択肢を設定
combobox["values"] = ["東京", "大阪", "名古屋", "福岡"]

# 初期選択を「東京」に設定
combobox.current(0)

# Comboboxを配置
combobox.pack(padx=10)

# 表示ボタンを作成（押下時にshow_input関数を呼び出す）
show_button = tk.Button(window, text="表示", command=show_input, font=("Arial", 12))
show_button.pack(pady=10)

# 結果表示用のラベルを作成（背景色と文字配置を指定）
result_label = tk.Label(window, text="", font=("Arial", 12), bg="lightyellow", justify="left", anchor="nw")

# 結果表示ラベルをウィンドウに配置（領域を広げて表示）
result_label.pack(fill="both", expand=True, padx=10, pady=10)

# イベントループを開始（ウィンドウを表示し、操作を待機）
window.mainloop()