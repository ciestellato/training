from django.db import models
from django.contrib.auth.models import User

class Topic(models.Model):
    """"ユーザーが学んでいるトピックを表す"""
    text = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    # 管理画面でレコードで表示される文字列
    def __str__(self):
        """モデルの文字列表現を返す"""
        return self.text

class Entry(models.Model):
    """トピックに関して学んだ具体的なこと"""
    # 外部キーで紐づけて、親トピックが削除されたら子エントリーも削除されるように設定
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'entries'
    
    def __str__(self):
        """モデルの文字列表現を返す"""
        msg = ""
        if(len(self.text) <= 25):
            msg = f"{self.text}"
        else:
            msg = f"{self.text[:50]}..."
        return msg