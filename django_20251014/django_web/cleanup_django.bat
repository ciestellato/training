@echo off
echo �N���[���A�b�v���J�n���܂�...

:: 1. ���z���t�H���_�ivenv�j���폜
echo.
echo ���z���t�H���_ (venv) ���폜��...
if exist "venv" (
    rmdir /s /q venv
    if not exist "venv" (
        echo �폜����: venv
    ) else (
        echo ?? �폜�Ɏ��s�������A�t�@�C�����g�p���ł�: venv
    )
) else (
    echo �t�H���_��������܂���: venv
)

:: 2. Python�L���b�V���t�H���_�i__pycache__�j���ꊇ�폜
echo.
echo Python�L���b�V���t�H���_ (__pycache__) �������E�폜��...
set "deleted_cache=0"
for /d /r . %%d in (__pycache__) do (
    if exist "%%d" (
        rmdir /s /q "%%d"
        echo �폜����: %%d
        set "deleted_cache=1"
    )
)
if "%deleted_cache%"=="0" (
    echo __pycache__ �t�H���_�͌�����܂���ł����B
)

:: 3. SQLite�f�[�^�x�[�X�t�@�C�� (db.sqlite3) ���폜
echo.
echo SQLite�f�[�^�x�[�X�t�@�C�� (db.sqlite3) ���폜��...
if exist "db.sqlite3" (
    del db.sqlite3
    if not exist "db.sqlite3" (
        echo �폜����: db.sqlite3
    ) else (
        echo ?? �폜�Ɏ��s�������A�t�@�C�����g�p���ł�: db.sqlite3
    )
) else (
    echo �t�@�C����������܂���: db.sqlite3
)

echo.
echo �N���[���A�b�v���������܂����B
pauses