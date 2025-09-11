"""
📝 演習問題（ファイル名：practice12.py）
引数に名前と年齢を受け取る関数を定義してください。年齢は省略可能で、デフォルトは30としてください。
関数を呼び出して、名前だけ渡した場合と、両方渡した場合の出力を確認してください。"""

def regist_member(name, age=30):
    print(f"{name}様({age})を登録しました")

regist_member("たぬき")
regist_member("ぽんちゃん", 55)