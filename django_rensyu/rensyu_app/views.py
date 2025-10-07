from django.http import HttpResponse

def home_view(request):
    return HttpResponse("これはホームページです。")

def profile_view(request):
    return HttpResponse("プロフィールページです。")

def profile_by_id(request, profile_id):
    return HttpResponse(f"ID {profile_id} のプロフィールです。")

def profile_by_email(request, profile_email):
    return HttpResponse(f"{profile_email} のプロフィールです。")

def about_view(request):
    return HttpResponse("<h2>このサイトについて</h2>Djangoのテストです。")