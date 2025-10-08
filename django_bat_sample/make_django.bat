@echo off
:: =======================================================
:: 変数定義
:: 変更したい場合は、以下の2行を修正してください。
:: =======================================================
SET PROJECT_ROOT=django_web
SET APP_NAME=calculator
:: =======================================================

:: 1. ルートディレクトリの作成と移動
mkdir %PROJECT_ROOT%
cd %PROJECT_ROOT%

:: 2. 仮想環境の作成と有効化
python -m venv venv
call venv\Scripts\activate.bat

:: 3. Djangoのインストールとプロジェクトの作成
pip install django
django-admin startproject conf .

:: 4. アプリケーションの作成
python manage.py startapp %APP_NAME%

:: 5. アプリケーション内の初期ファイルの作成
echo.
echo === App initial file creation in progress... ===

:: urls.pyの作成
:: ファイルパス: %APP_NAME%\urls.py
(
    echo from django.urls import path
    echo from . import views
    echo.
    echo app_name = "%APP_NAME%"
    echo urlpatterns = [
    echo     path('', views.index, name='index'),
    echo ]
)> %APP_NAME%\urls.py

:: テンプレートディレクトリの作成
:: フォルダパス: %APP_NAME%\templates\%APP_NAME%
mkdir %APP_NAME%\templates\%APP_NAME%

:: index.htmlの作成（英語コンテンツ）
:: ファイルパス: %APP_NAME%\templates\%APP_NAME%\index.html
(
    echo ^<!DOCTYPE html^>
    echo ^<html lang="en"^>
    echo ^<head^>
    echo     ^<meta charset="UTF-8"^>
    echo     ^<title^>^^%APP_NAME^^% Index Page^</title^>
    echo ^</head^>
    echo ^<body^>
    echo     ^<h1^>Welcome to the ^^%APP_NAME^^% Application!^</h1^>
    echo     ^<p^>This is the automatically generated index.html file.^</p^>
    echo ^</body^>
    echo ^</html^>
)> %APP_NAME%\templates\%APP_NAME%\index.html

:: 完了メッセージ
echo.
echo =======================================================
echo Django project setup is complete!
echo Root Directory Name: %PROJECT_ROOT%
echo Application Name: %APP_NAME%
echo - %APP_NAME%\urls.py was created.
echo - %APP_NAME%\templates\%APP_NAME%\index.html was created.
echo The Django virtual environment is active.
echo Type deactivate to exit.
echo =======================================================