from django.urls import path
from . import views

app_name = 'session'

urlpatterns = [
    path('set/', views.set_session_view, name='set_session'),# <a href="{% url 'session:set_session' %}">セッションに値を保存</a>
    path('get/', views.get_session_view, name='get_session'),# <a href="{% url 'session:get_session' %}">セッションから値を取得</a>
    path('delete/', views.delete_session_view, name='delete_session'),# <a href="{% url 'session:delete_session' %}">セッションから値を削除</a>
]