from django.shortcuts import render, HttpResponse

# Create your views here.
# user


def test(request):
    # test動作用 path('test/', views.test, name='test'),
    return HttpResponse("user:test")


def register_user(request):
    # ユーザ登録 path('register/', views.register_user, name='register'),
    pass


def thanks(request):
    # ユーザ登録完了 path('thanks/', views.thanks, name='thanks'),
    pass
