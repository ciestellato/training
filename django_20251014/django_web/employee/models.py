from django.db import models

# 部署情報を格納するモデルクラス
class Dept(models.Model):
    name = models.CharField(max_length=100, verbose_name='部署名')  # 部署名フィールド

    def __str__(self):
        return self.name  # 管理画面などで部署名を表示

# 従業員情報を格納するモデルクラス
class Emp(models.Model):
    name = models.CharField(max_length=100, verbose_name='氏名')  # 従業員の名前
    age = models.IntegerField(verbose_name='年齢')  # 年齢
    # ForeignKeyでDeptモデルと関連付け（1対多）。部署が削除されたら従業員も削除される。
    dept = models.ForeignKey(Dept, on_delete=models.CASCADE, verbose_name='所属部署')  

    def __str__(self):
        return f"{self.name}（{self.dept.name}）"  # 管理画面などで氏名と部署名を表示