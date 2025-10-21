from django.shortcuts import render

# Create your views here.
def index(request):
    """学習ノートのホームページ"""
    return render(request, 'learning_logs/index.html')