from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request,'home/index.html')

# Djangoの基本ビュークラスとレンダリング関数をインポート
from django.views import View
from django.shortcuts import render, redirect
from .forms import ContactForm

# クラスベースビューでフォーム処理を行うビューを定義
class ContactView(View):
    # GETリクエスト時：フォームを表示
    def get(self, request):
        form = ContactForm()  # 空のフォームを作成
        return render(request, 'home/contact.html', {'form': form})  # テンプレートにフォームを渡して表示

    # POSTリクエスト時：フォーム送信処理
    def post(self, request):
        form = ContactForm(request.POST)  # 送信されたデータをフォームに渡す
        if form.is_valid():  # バリデーションチェック
            # フォームのデータを取得（ここでは表示のみ）
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            # 実際にはメール送信やDB保存などを行う
            return render(request, 'home/thanks.html', {'name': name})  # 完了ページを表示
        else:
            # バリデーションエラーがある場合はフォームを再表示
            return render(request, 'home/contact.html', {'form': form})