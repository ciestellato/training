# Djangoのフォーム機能を使うためにインポート
from django import forms

# お問い合わせフォームを定義。データベースのテーブルと連携しない単なる画面入力項目生成用
class ContactForm(forms.Form):
    name = forms.CharField(label='Your Name', max_length=100)  # 名前入力欄
    email = forms.EmailField(label='Email')                    # メールアドレス入力欄
    message = forms.CharField(label='Message', widget=forms.Textarea)  # メッセージ欄（複数行）