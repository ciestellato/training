import tkinter as tk


def get_center_positon(win_width, win_height, window):
    """ウインドウをディスプレイの中央に配置する位置を取得する
    引数：ウィンドウサイズの指定"""

    # 画面サイズを取得
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # 中央位置を計算
    x = (screen_width // 2) - (win_width // 2)
    y = (screen_height // 2) - (win_height // 2)

    # geometryでサイズと位置を設定
    return f"{win_width}x{win_height}+{x}+{y}"
