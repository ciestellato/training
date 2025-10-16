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
]
