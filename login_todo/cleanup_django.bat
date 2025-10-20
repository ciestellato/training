@echo off
echo クリーンアップを開始します...

:: 1. 仮想環境フォルダ（venv）を削除
echo.
echo 仮想環境フォルダ (venv) を削除中...
if exist "venv" (
    rmdir /s /q venv
    if not exist "venv" (
        echo 削除完了: venv
    ) else (
        echo ?? 削除に失敗したか、ファイルが使用中です: venv
    )
) else (
    echo フォルダが見つかりません: venv
)

:: 2. Pythonキャッシュフォルダ（__pycache__）を一括削除
echo.
echo Pythonキャッシュフォルダ (__pycache__) を検索・削除中...
set "deleted_cache=0"
for /d /r . %%d in (__pycache__) do (
    if exist "%%d" (
        rmdir /s /q "%%d"
        echo 削除完了: %%d
        set "deleted_cache=1"
    )
)
if "%deleted_cache%"=="0" (
    echo __pycache__ フォルダは見つかりませんでした。
)

:: 3. SQLiteデータベースファイル (db.sqlite3) を削除
echo.
echo SQLiteデータベースファイル (db.sqlite3) を削除中...
if exist "db.sqlite3" (
    del db.sqlite3
    if not exist "db.sqlite3" (
        echo 削除完了: db.sqlite3
    ) else (
        echo ?? 削除に失敗したか、ファイルが使用中です: db.sqlite3
    )
) else (
    echo ファイルが見つかりません: db.sqlite3
)

echo.
echo クリーンアップが完了しました。
pauses