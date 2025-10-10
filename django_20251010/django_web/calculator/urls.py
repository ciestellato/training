from django.urls import path
from . import views

app_name = 'calculator'

urlpatterns = [
    # test動作用
    path('test/', views.test, name='test'),
    path('bmi/', views.bmi_view, name='bmi'),
]
