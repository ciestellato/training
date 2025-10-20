from django.urls import path
from . import views

app_name = 'todo'

urlpatterns = [
    path('list', views.todo_list, name='list'),  # 一覧表示
    path('create/', views.todo_create, name='create'),  # 新規作成

]
