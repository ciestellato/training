from django.db import models

# Create your models here.
# 話題テーブルの定義
class Topic(models.Model):
    text = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        "モデルの文字列表現を返す"
        return self.text

class Entry(models.Model):
    """トピックに関して学んだ具体的なこと"""
    # ForeignKey(外部キー)のインスタンス
    # on_delete=models.CASCADE) Topicを削除すると連鎖してEntryも削除する
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    # Metaクラスはモデルを管理するための追加情報を保持する
    # 今回は、複数形を「Entrys」ではなく「Entries」を使うよう指示
    class Meta:
        verbose_name_plural = 'entries'
    
    def __str__(self):
        """モデルの文字列型表現を返す"""
        return  f"{self.text[:50]}..."