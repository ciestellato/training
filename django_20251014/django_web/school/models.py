from django.db import models

# 学生モデル
class Student(models.Model):
    # 学生の名前を保持するフィールド
    name = models.CharField(max_length=100, verbose_name="学生名")

    # 管理画面などでオブジェクトを識別するための文字列表現を返す
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "学生"
        verbose_name_plural = "学生"

# 試験モデル
class Exam(models.Model):
    # 試験の名称を保持するフィールド
    name = models.CharField(max_length=100, verbose_name="試験名")
    # 試験の日付を保持するフィールド
    date = models.DateField(verbose_name="実施日")

    # 管理画面などでオブジェクトを識別するための文字列表現を返す
    def __str__(self):
        # 試験名と日付を組み合わせて返す
        return f"{self.name} ({self.date})"

    class Meta:
        verbose_name = "試験"
        verbose_name_plural = "試験"

# 成績モデル (学生と試験への外部キーを持つ)
class Score(models.Model):
    # 学生モデルへの外部キー (1人の学生が複数の成績を持つ = 1対多の関係)
    # on_delete=models.CASCADE は、関連する学生が削除された場合にこの成績も削除することを意味する
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        verbose_name="学生"
    )
    # 試験モデルへの外部キー (1つの試験が複数の成績を持つ = 1対多の関係)
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        verbose_name="試験"
    )
    # 点数を保持するフィールド
    score = models.IntegerField(verbose_name="点数")

    def __str__(self):
        # 成績の文字列表現
        return f"{self.student.name} の {self.exam.name} の成績"

    class Meta:
        verbose_name = "成績"
        verbose_name_plural = "成績"
        # 同じ学生が同じ試験を複数回受けないようにするための制約 (一意性の設定)
        unique_together = ('student', 'exam')