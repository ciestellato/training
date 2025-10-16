from django.urls import path
from . import views

app_name = 'school'

urlpatterns = [
    # テスト
    # path('test/', views.test_veiw, name='test'),  # {% url 'employee:test' %}
    # path('emp_create/', views.emp_create, name='emp_create'),  # 従業員登録画面
    # path('emp_list/', views.emp_list, name='emp_list'),
    path('score_create/', views.score_create_view, name='score_create'),
    path('exam_create/', views.exam_create_view, name='exam_create'),
    
    # def exam_record_list_edit_delete(request): 編集・削除リンク付き一覧画面
    path('exam_record_list_edit_delete/', views.exam_record_list_edit_delete,
        name='exam_record_list_edit_delete'),

    # examレコードの編集画面へのルート
    # <int:id> は対象レコードのIDをURLから取得するためのパラメータ
    path('exam_record_edit/<int:id>/',
        views.exam_record_edit, name='exam_record_edit'),

    # examレコードの削除確認・処理画面へのルート
    # <int:id> は削除対象のレコードIDを指定
    path('exam_record_delete/<int:id>/',
        views.exam_record_delete, name='exam_record_delete'),
]
