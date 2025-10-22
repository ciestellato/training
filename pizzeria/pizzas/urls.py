from django.urls import path

from . import views

app_name = 'pizzas'

urlpatterns = [
    # ホームページ
    path('', views.index, name='index'),
    # ピザ一覧
    path('pizzas/', views.pizzas, name='pizzas'),
    # ピザのトッピング
    path('pizzas/<int:pizza_id>/', views.pizza, name='pizza'),
]