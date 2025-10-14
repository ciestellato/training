from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    # test動作用
    path('test/', views.test, name='test'),
    # ユーザ登録
    path('register/', views.register_user, name='register'),
    # ユーザ登録完了
    path('thanks/', views.thanks, name='thanks'),

]
