@echo off
echo 配布されたDjangoの仮想環境のセットアップを開始します。

REM 仮想環境を作成
python -m venv venv

REM 仮想環境を有効化
call venv\Scripts\activate

REM 依存パッケージをインストール
pip install -r requirements.txt

REM ------------------------------------------------------------------
REM モデル変更を検出してマイグレーションファイルを作成
echo.
echo モデル変更を検出してマイグレーションファイルを作成します...
python manage.py makemigrations

REM データベースにマイグレーションを適用
echo.
echo データベースにマイグレーションを適用します...
python manage.py migrate
REM ------------------------------------------------------------------

REM 終了メッセージ
echo.
echo 仮想環境のセットアップと初期マイグレーションが完了しました。
pause