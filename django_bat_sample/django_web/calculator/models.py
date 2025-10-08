from django.db import models

# Create your models here.
# 話題テーブルの定義
class Topic(models.Model):
    text = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        "モデルの文字列表現を返す"
        return self.text