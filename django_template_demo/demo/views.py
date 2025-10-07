from django.shortcuts import render  # テンプレート表示用関数

# indexビュー関数を定義
def index(request):
    # モデルを使わず、Pythonのデータを直接テンプレートに渡す
    context = {
        'user_name': '鈴木太郎',  # 変数表示の例
        'score': 92,  # 条件分岐の例
        'messages': ['ようこそ！', 'Djangoを楽しもう', 'Safe設計を意識しよう'],  # 繰り返し表示の例
        'show_score': True,  # 条件表示の制御
    }
    return render(request, 'demo/index.html', context)  # テンプレートにデータを渡して表示
