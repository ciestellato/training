from django.shortcuts import render # HTMLテンプレートを表示する関数

# Create your views here.

def index(request):
	from calculator.models import Topic

	topics = Topic.objects.all()
	for topic in topics:
		print(topic.id,topic)
	return render(request, 'calculator/index.html', {'topics': topics})

def bmi_view(request):  # BMI計算ページのビュー関数
    bmi = None  	# 初期状態ではBMIは未計算
    nick_name = ""	# 初期状態では空文字
    if request.method == 'POST':  # フォームが送信されたとき
        nick_name = request.POST['nick_name']	# 名前を取得
        height = float(request.POST['height'])  # 身長を取得（cm）
        weight = float(request.POST['weight'])  # 体重を取得（kg）
        height_m = height / 100  # cm → m に変換
        bmi = round(weight / (height_m ** 2), 2)  # BMI計算（小数第2位まで）

    # GET,POSTともにbmi.htmlを表示
    return render(request, 'calculator/bmi.html', {'bmi': bmi, 'nick_name': nick_name})  # テンプレートにBMIを渡す