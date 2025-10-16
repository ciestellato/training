from django.shortcuts import render, redirect
from .forms import ScoreForm, ExamForm
from school.models import Exam
from django.contrib import messages
from django.shortcuts import get_object_or_404

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

def exam_record_list_edit_delete(request):
    # 編集・削除リンク付き一覧画面
    records = Exam.objects.all().order_by('-date', '-id')  # 新しい順に並べる
    return render(request, 'school/exam_list_edit_delete.html', {'records': records})

def exam_record_edit(request, id):
    # idで検索
    record = get_object_or_404(Exam, pk=id)

    # ボタンを押された
    if request.method == 'POST':
        # POSTデータと既存のレコードを使ってフォームを生成（instance指定で更新モードになる）。
        form = ExamForm(request.POST, instance=record)

        # フォームのバリデーション（入力チェック）を実行。
        if form.is_valid():
            # 入力が正しければ、フォームの内容でレコードを保存（更新）。
            form.save()

            # 更新成功メッセージを表示（テンプレート側で messages を使って表示可能。 ※messagesは自動でhtmlに渡される）。
            messages.success(request, '更新しました')

            # 一覧画面にリダイレクト（URL名 'school:exam_record_list_edit_delete' が定義されている必要あり）。
            return redirect('school:exam_record_list_edit_delete')

    # 編集フォーム入力内容に検索レコードをセット：オブジェクト生成
    form = ExamForm(instance=record)

    # フォームをテンプレートに渡して表示。テンプレート 'school:exam_form.html' を使用。
    return render(request, 'school/exam_edit_form.html', {'form': form})


def exam_record_delete(request, id):
    # 指定されたIDに対応するBmiRecordオブジェクトを取得。存在しない場合は404エラー画面を表示。
    record = get_object_or_404(Exam, pk=id)
    # 削除
    # リクエストがPOST（削除ボタンが押された）だった場合、削除処理を実行する。
    if request.method == 'POST':
        # 対象のレコードをデータベースから削除する。
        record.delete()

        # 削除成功メッセージを表示（テンプレート側で messages を使って表示可能）。
        messages.success(request, '削除しました')

        # 一覧画面にリダイレクト（URL名 'school:exam_record_list_edit_delete' が定義されている必要あり）。
        return redirect('school:exam_record_list_edit_delete')
    
    # GETリクエストの場合（削除確認画面の表示）、対象レコードをテンプレートに渡して表示。
    return render(request, 'school/exam_confirm_delete.html', {'record': record})