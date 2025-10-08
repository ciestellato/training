from django.urls import path
from . import views
app_name = 'calculator'

urlpatterns = [
	# test動作用
	path('index/', views.index, name='index'),
]