from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    # 全体のホームページ（各アプリへのリンクを表示）
    path('', views.index, name='index'),  # {% url 'home:index' %}
    # messageテスト
    path('message/', views.message_veiw, name='message'),  # {% url 'home:message' %}
]
