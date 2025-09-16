import tkinter as tk  # Tkinterの基本GUIモジュールをインポート
from tkinter import ttk  # ttkモジュール（スタイル付きウィジェット）をインポート

# ボタン押下時に入力内容を取得してラベルに表示する関数
def show_contact():
    # Entryウィジェットからメールアドレスを取得
    email = email_entry.get()
    
    # Textウィジェットから問い合わせ内容を取得（1.0は1行目の先頭、tk.ENDは末尾）
    inquiry = inquiry_text.get("1.0", tk.END).strip()  # strip()で末尾の改行を除去
    
    # ラベルに取得した内容を表示（改行で分けて整形）
    result_label.config(text=f"メール: {email}\n問い合わせ: {inquiry}")

# メインウィンドウを作成
window = tk.Tk()

# ウィンドウのタイトルを設定
window.title("問い合わせフォーム")

# メールアドレス入力用のラベルを作成し、左寄せで配置
tk.Label(window, text="メールアドレス:").pack(anchor="w", padx=10)

# メールアドレス入力欄（Entryウィジェット）を作成し、配置
email_entry = tk.Entry(window, width=40)
email_entry.pack(padx=10)

# 問い合わせ内容入力用のラベルを作成し、左寄せで配置
tk.Label(window, text="問い合わせ内容:").pack(anchor="w", padx=10)

# 問い合わせ内容入力欄（Textウィジェット）を作成し、配置
inquiry_text = tk.Text(window, width=40, height=5)
inquiry_text.pack(padx=10)

# 送信ボタン（ttkスタイル）を作成し、押下時に show_contact 関数を呼び出す
ttk.Button(window, text="送信", command=show_contact).pack(pady=10)

# 結果表示用のラベルを作成（背景色と文字配置を指定）
result_label = tk.Label(window, text="", bg="lightyellow", justify="left")

# 結果表示ラベルをウィンドウに配置（fillとexpandで領域を広げる）
result_label.pack(fill="both", expand=True, padx=10, pady=10)

# イベントループを開始（ウィンドウを表示し、操作を待機）
window.mainloop()