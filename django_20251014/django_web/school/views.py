from django.shortcuts import render, redirect
from .forms import ScoreForm, ExamForm

# 成績登録ビューの定義
def score_create_view(request):
    # HTTPメソッドがPOST (フォームが送信された) の場合
    if request.method == 'POST':
        # 送信されたデータを使ってフォームを初期化
        form = ScoreForm(request.POST)
        # フォームのバリデーション (入力チェック) を実行
        if form.is_valid():
            # バリデーションが成功した場合、データをデータベースに保存
            form.save()
            # フォーム送信後、別のページ（例: 成績一覧ページなど）にリダイレクト
            # この例では簡単のため、このページにリダイレクト
            return redirect('school:score_create')
    # HTTPメソッドがGET (ページが初めて表示された) の場合、またはバリデーションエラーの場合
    else:
        # 空のフォームを初期化
        form = ScoreForm()

    # フォームをテンプレートに渡して描画
    context = {'form': form, 'title': '成績登録フォーム'}
    # 'score_form.html' テンプレートを使ってレンダリング
    return render(request, 'school/score_form.html', context)


# 試験登録ビューの定義
def exam_create_view(request):
    # HTTPメソッドがPOST (フォームが送信された) の場合
    if request.method == 'POST':
        # 送信されたデータを使ってフォームを初期化
        form = ExamForm(request.POST)
        # フォームのバリデーション (入力チェック) を実行
        if form.is_valid():
            # バリデーションが成功した場合、データをデータベースに保存
            form.save()
            # フォーム送信後、別のページ（例: 成績一覧ページなど）にリダイレクト
            # この例では簡単のため、このページにリダイレクト
            return redirect('school:exam_create')
    # HTTPメソッドがGET (ページが初めて表示された) の場合、またはバリデーションエラーの場合
    else:
        # 空のフォームを初期化
        form = ExamForm()

    # フォームをテンプレートに渡して描画
    context = {'form': form, 'title': '試験登録フォーム'}
    # 'exam_form.html' テンプレートを使ってレンダリング
    return render(request, 'school/exam_form.html', context)