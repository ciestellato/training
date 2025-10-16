from django.urls import path
from . import views

app_name = 'employee'

urlpatterns = [
    # テスト
    path('test/', views.test_veiw, name='test'),  # {% url 'employee:test' %}
]
