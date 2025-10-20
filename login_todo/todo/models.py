from django.db import models

# Create your models here.
# Djangoの組み込みユーザーモデルをインポート
from django.contrib.auth.models import User

# Todoモデルを定義（1つのタスクを表す）


class Todo(models.Model):
    # タスクを作成したユーザーと紐づけ（1対多の関係）
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # タスクのタイトル（最大100文字）
    title = models.CharField(max_length=100)
    # タスクの詳細（空でもOK）
    description = models.TextField(blank=True)
    # タスクが完了しているかどうか（Trueなら完了）
    is_finished = models.BooleanField(default=False)
    # タスクの作成日時（自動で現在時刻が入る）
    created_at = models.DateTimeField(auto_now_add=True)

    # 管理画面などで表示される文字列
    def __str__(self):
        return self.title
