# 必要な関数をインポート（テンプレート表示やリダイレクトに使用）
from django.shortcuts import render, redirect

# セッションに値を保存するビュー関数
def set_session_view(request):
    # セッションにキーと値を保存（ここでは 'username' に 'taro' を保存）
    request.session['username'] = 'taro'
    # メッセージを表示するためのテンプレートを返す
    return render(request, 'session/set.html')

# セッションから値を取得するビュー関数
def get_session_view(request):
    # セッションから 'username' の値を取得（存在しない場合は None）
    username = request.session.get('username')
    # テンプレートに取得した値を渡して表示
    return render(request, 'session/get.html', {'username': username})

# セッションの値を削除するビュー関数
def delete_session_view(request):
    # 'username' キーがセッションに存在する場合は削除
    if 'username' in request.session:
        del request.session['username']
    # 削除後の確認用テンプレートを表示
    return render(request, 'session/delete.html')