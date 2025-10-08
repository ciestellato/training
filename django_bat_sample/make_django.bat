@echo off
:: =======================================================
:: �ϐ���`
:: �ύX�������ꍇ�́A�ȉ���2�s���C�����Ă��������B
:: =======================================================
SET PROJECT_ROOT=django_web
SET APP_NAME=calculator
:: =======================================================

:: 1. ���[�g�f�B���N�g���̍쐬�ƈړ�
mkdir %PROJECT_ROOT%
cd %PROJECT_ROOT%

:: 2. ���z���̍쐬�ƗL����
python -m venv venv
call venv\Scripts\activate.bat

:: 3. Django�̃C���X�g�[���ƃv���W�F�N�g�̍쐬
pip install django
django-admin startproject conf .

:: 4. �A�v���P�[�V�����̍쐬
python manage.py startapp %APP_NAME%

:: 5. �A�v���P�[�V�������̏����t�@�C���̍쐬
echo.
echo === App initial file creation in progress... ===

:: urls.py�̍쐬
:: �t�@�C���p�X: %APP_NAME%\urls.py
(
    echo from django.urls import path
    echo from . import views
    echo.
    echo app_name = "%APP_NAME%"
    echo urlpatterns = [
    echo     path('', views.index, name='index'),
    echo ]
)> %APP_NAME%\urls.py

:: �e���v���[�g�f�B���N�g���̍쐬
:: �t�H���_�p�X: %APP_NAME%\templates\%APP_NAME%
mkdir %APP_NAME%\templates\%APP_NAME%

:: index.html�̍쐬�i�p��R���e���c�j
:: �t�@�C���p�X: %APP_NAME%\templates\%APP_NAME%\index.html
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

:: �������b�Z�[�W
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