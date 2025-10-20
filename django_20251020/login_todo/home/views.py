from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm


def index(request):
    return render(request, 'home/index.html')

# ログインしていないとアクセスできないビュー


@login_required
def mypage(request):
    # ログインユーザー情報は request.user に格納されている
    return render(request, 'home/mypage.html')


def register(request):
    # ユーザー登録ビュー
    pass
