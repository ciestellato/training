import tkinter as tk


def update_text_area():
    # 一度クリア
    text_area.delete("1.0", tk.END)
    # サンプルデータ
    sample_list = ["Python", "SQLite", "SQLAlchemy", "Tkinter"]
    # リストデータを繰り返し挿入
    for item in sample_list:
        text_area.insert(tk.END, f"{item}\n")


def clear_text_area():
    # 一度クリア
    text_area.delete("1.0", tk.END)


# GUI構築
window = tk.Tk()
window.title("Textエリア更新デモ")

text_area = tk.Text(window, height=10, width=40)
text_area.pack(padx=10, pady=10)
text_area.insert("1.0", "検索結果をここに表示します")

# ボタンで更新
update_button = tk.Button(
    window, text="更新", command=update_text_area)
update_button.pack(pady=5)

clear_button = tk.Button(
    window, text="クリア", command=clear_text_area)
clear_button.pack(pady=5)

# ボタンを配置して、クリックでウィンドウを閉じる
tk.Button(window, text="閉じる", bg="red", fg="white",
          command=window.destroy).pack(pady=5)

window.mainloop()
