from django.shortcuts import render

# Create your views here.
def index(request):
    """ピザのホームページ"""
    return render(request, 'pizzas/index.html')