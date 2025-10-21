from django.urls import path
from . import views
from .views import ContactView


app_name = 'home'

urlpatterns = [
    # ルート/
    path('', views.index, name='index'),
    path('contact/', ContactView.as_view(), name='contact'),  # クラスベースビューを関数として登録
]
