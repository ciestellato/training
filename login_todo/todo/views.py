from django.shortcuts import render, redirect
from .forms import TodoForm
from .models import Todo
# ログインしていないとアクセスできないようにするデコレータ
from django.contrib.auth.decorators import login_required
# Create your views here.

# ●以下はログインが必要な処理

def todo_create(request):
    # ログインユーザーに紐づいたタスクを登録する（insert todos）
    pass

def todo_list(request):
    # ログインユーザーに紐づいたタスクを取得し、作成日時の降順で並べる
    pass
