from django.urls import path
from . import views
app_name = 'calculator'

urlpatterns = [
	# calculator/index/
	path('index/', views.index, name='index'),
    # calculator/
    path('', views.bmi_view, name='bmi'),
]