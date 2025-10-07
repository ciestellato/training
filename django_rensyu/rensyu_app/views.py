from django.http import HttpResponse

def home_view(request):
    return HttpResponse("これはホームページです。")

def profile_view(request):
    return HttpResponse("プロフィールページです。")

def about_view(request):
    return HttpResponse("<h2>このサイトについて</h2>Djangoのテストです。")