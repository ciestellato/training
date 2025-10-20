# Djangoのフォーム機能を使うためにインポート
from django import forms
# Todoモデルをインポート
from .models import Todo


class TodoForm(forms.ModelForm):
    # Todoモデルに基づいたフォームを定義
    pass
