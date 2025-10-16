from django import forms
from .models import Score, Exam

# Scoreモデルに基づくフォームを定義する
class ScoreForm(forms.ModelForm):
    # このフォームがScoreモデルと対応することを指定
    class Meta:
        model = Score
        # フォームに表示したいフィールドを指定
        # 'student'と'exam'は外部キーなので、自動でドロップダウンリストになる
        fields = ['student', 'exam', 'score']
        # フィールドの表示順序やウィジェットをカスタマイズしたい場合はここに記述

        # 例: scoreフィールドのウィジェットをカスタマイズ
        # widgets = {
        #     'score': forms.NumberInput(attrs={'min': 0, 'max': 100}),
        # }


# Examモデルに基づくフォームを定義する
class ExamForm(forms.ModelForm):
    # このフォームがScoreモデルと対応することを指定
    class Meta:
        model = Exam
        # フォームに表示したいフィールドを指定
        fields = ['name', 'date']
        # フィールドの表示順序やウィジェットをカスタマイズしたい場合はここに記述
