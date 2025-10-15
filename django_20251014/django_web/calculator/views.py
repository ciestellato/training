from .models import BmiRecord
from django.shortcuts import render
from .forms import BmiRecordForm
from .forms import BmiForm  # BmiForm をインポート
from django.shortcuts import render, HttpResponse
from .forms import ProfileForm

# Create your views here.
def hello_view(request):
    simei = None # HTMLに渡すデータ
    form = None # HTMLに渡すデータ
    if request.method == 'POST':  # フォームがPOST送信された
        # フォームを生成,全送信データをセット
        form = ProfileForm(request.POST)
        # 値のチェック
        if form.is_valid():
            # 適正データ
            simei = form.cleaned_data['simei']

    # GET＝アドレス指定でアクセス
    else:
        # 空のフォームオブジェクト
        form = ProfileForm()
    return render(request, 'calculator/hello.html', {'form':form, 'simei':simei,} )


def test(request):
    return HttpResponse("test page OK.")


def bmi_view(request):
    # BMI計算ページのビュー関数
    context = None  # HTMLに渡すデータ辞書

    if request.method == 'POST':  # フォームがPOST送信されたとき
        simei = request.POST['simei']  # お名前を取得
        height = float(request.POST['height'])  # 身長を取得して小数に変換（cm）
        weight = float(request.POST['weight'])  # 体重を取得して小数に変換（kg）
        height_m = height / 100  # cm → m に変換
        bmi = round(weight / (height_m ** 2), 2)  # BMI計算（小数第2位まで）
        context = {'simei': simei,
                   'height': height,
                   'weight': weight, 'bmi': bmi
                   }

    # GET,POSTともにbmi.htmlを表示
    return render(request, template_name='calculator/bmi.html', context=context)


def bmi_form(request):
    # BMI計算フォームクラスで処理するビュー関数
    result = None  # 初期化：計算結果を格納する変数（テンプレートに渡す用）

    # フォームが送信されたかどうかを判定（POSTメソッドかどうか）
    if request.method == 'POST':
        # POSTデータを使ってフォームをインスタンス化（バリデーション対象）
        form = BmiForm(request.POST)

        # フォームの入力がすべて有効かどうかをチェック
        if form.is_valid():
            # バリデーション済みのデータを取得（辞書形式）
            simei = form.cleaned_data['simei']     # お名前
            height = form.cleaned_data['height']   # 身長（cm）
            weight = form.cleaned_data['weight']   # 体重（kg）

            # 身長をメートルに変換（cm → m）
            height_m = height / 100

            # BMIを計算（体重 ÷ 身長²）
            bmi = round(weight / (height_m ** 2), 2)

            # 結果メッセージを作成
            result = f"{simei} さんのBMIは {bmi} です。"

    else:
        # GETリクエストの場合は空のフォームを表示
        form = BmiForm()

    # form.html テンプレートを表示し、フォームと結果を渡す
    return render(request, 'calculator/BmiForm.html', {'form': form, 'result': result})


def bmi_record_form(request):
    # BMIモデルフォームクラスを利用したデータベース登録処理
    if request.method == 'POST':
        form = BmiRecordForm(request.POST)
        if form.is_valid():
            record = form.save()  # データベースに保存
            bmi_value = record.bmi()  # BMIを計算
            return render(request, 'calculator/BmiRecordForm.html', {
                'form': form,
                'bmi': bmi_value,
                'record': record,
                'submitted': True
            })
    else:
        form = BmiRecordForm()
    return render(request, 'calculator/BmiRecordForm.html', {
        'form': form,
        'submitted': False
    })


def bmi_record_list(request):
    # BmiRecordsテーブルの一覧
    records = BmiRecord.objects.all().order_by('-id')  # 新しい順に並べる
    return render(request, 'calculator/bmi_list.html', {'records': records})


def bmi_record_list_edit_delete(request):
    # 編集・削除リンク付き一覧画面
    records = BmiRecord.objects.all().order_by('-id')  # 新しい順に並べる
    return render(request, 'calculator/bmi_list_edit_delete.html', {'records': records})


def bmi_record_edit(request, id):
    # 編集
    return HttpResponse(f'id:{id}のレコードを[編集]します')


def bmi_record_delete(request, id):
    # 削除
    return HttpResponse(f'id:{id}のレコードを[削除]します')
