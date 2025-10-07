from django.urls import path  # URL定義用
from . import views  # views.py をインポート

urlpatterns = [
    path('', views.index, name='index'),  # ルートURLに index 関数を割り当て
]