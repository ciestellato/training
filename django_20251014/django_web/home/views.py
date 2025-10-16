from django.shortcuts import render
from django.contrib import messages


# Create your views here.

# プロジェクト全体のホームページを表示


def index(request):
    return render(request, 'home/index.html')

def message_veiw(request):
    messages.success(request, "保存が完了しました！")
    messages.error(request, "エラーが発生しました。")
    return render(request, 'home/message.html')
