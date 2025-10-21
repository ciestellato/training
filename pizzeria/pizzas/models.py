from django.db import models

# Create your models here.
class Pizza(models.Model):
    """ピザのモデルクラス"""
    name = models.CharField(max_length=50)
    date_added = models.DateTimeField(auto_now_add=True)
    
    # 管理画面でレコードで表示される文字列
    def __str__(self):
        """モデルの文字列表現を返す"""
        return self.name

class Topping(models.Model):
    """トッピングのモデルクラス"""
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    date_added = models.DateTimeField(auto_now_add=True)
    
    # 管理画面でレコードで表示される文字列
    def __str__(self):
        """モデルの文字列表現を返す"""
        return self.name