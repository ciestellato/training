"""learning_logsのURLパターンの定義"""

from django.urls import path

from . import views

app_name = 'learning_logs'

urlpatterns = [
    # ホームページ
    path('', views.index, name='index'),
    # すべてのトピックを表示するページ
    path('topics/', views.topics, name='topics'),
    # 個別トピックの詳細ページ
    path('topics/<int:topic_id>/', views.topic, name='topic'),

    # 新規トピック追加ページ
    path('new_topic/', views.new_topic, name='new_topic'),
]