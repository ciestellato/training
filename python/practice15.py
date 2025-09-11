"""
📝 演習問題（ファイル名：practice15.py）
任意のキーワード引数を受け取り、それらを「○○(キーワード)は△△（値）です」という形式で表示する関数を定義してください。
関数を呼び出して、color="赤", size="M", stock=12 を渡して表示してください。"""

# ユーザー情報（名前・年齢・職業など）をキーワード引数で受け取り、整形して表示する関数
def show_user_info(**info):
    for key, value in info.items():
        print(f"{key}: {value}")  # 各項目を表示

# 関数を呼び出して情報を表示
show_user_info(color="赤", size="M", stock=12)