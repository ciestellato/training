@echo off
echo 配布されたDjangoの仮想環境のセットアップを開始します。
REM 仮想環境を作成
python -m venv venv

REM 仮想環境を有効化
call venv\Scripts\activate

REM 依存パッケージをインストール
pip install -r requirements.txt

REM 終了メッセージ
echo 仮想環境のセットアップが完了しました。
pause