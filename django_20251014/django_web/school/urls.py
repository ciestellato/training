from django.urls import path
from . import views

app_name = 'school'

urlpatterns = [
    # テスト
    # path('test/', views.test_veiw, name='test'),  # {% url 'employee:test' %}
    # path('emp_create/', views.emp_create, name='emp_create'),  # 従業員登録画面
    # path('emp_list/', views.emp_list, name='emp_list'),
]
