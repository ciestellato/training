"""accountsのURLパターンの定義"""

from django.urls import path, include

from . import views

app_name = 'accounts'

urlpatterns = [
    # デフォルトの認証URL
    path('', include('django.contrib.auth.urls')),
    # ユーザー登録ページ
    path('register/', views.register, name='register'),
]