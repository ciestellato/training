from django.urls import path
from . import views


app_name = 'home'

urlpatterns = [
    # ルート/
    path('', views.index, name='index'),
 
]
