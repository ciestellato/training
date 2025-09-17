# main_menu.py
import tkinter as tk
from sub_kensaku_window import launch_sub_kensaku_window  # 既存ウィンドウの関数をインポート
from center_position import get_center_positon

window = tk.Tk()
window.title("メインメニュー")
# ディスプレイの中央位置に配置する関数を使う
window.geometry(get_center_positon(400, 300, window))

tk.Button(window, text="サブウィンドウを開く", command=launch_sub_kensaku_window).pack()

window.mainloop()
