"""accountsのURLパターンの定義"""

from django.urls import path, include

app_name = 'accounts'

urlpatterns = [
    # デフォルトの認証URL
    path('', include('django.contrib.auth.urls')),
]