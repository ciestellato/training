from django.shortcuts import render, HttpResponse

# Create your views here.


def test(request):
    return HttpResponse("test page OK.")


def bmi_view(request):  # BMI計算ページのビュー関数
    context = None  # HTMLに渡すデータ辞書

    if request.method == 'POST':  # フォームが送信されたとき
        height = float(request.POST['height'])  # 身長を取得（cm）
        weight = float(request.POST['weight'])  # 体重を取得（kg）
        height_m = height / 100  # cm → m に変換
        bmi = round(weight / (height_m ** 2), 2)  # BMI計算（小数第2位まで）
        context = {'height': height, 'weight': weight, 'bmi': bmi}

    # GET,POSTともにbmi.htmlを表示
    return render(request, template_name='calculator/bmi.html', context=context)
