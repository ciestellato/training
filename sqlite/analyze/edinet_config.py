import os
import time
import requests
import pandas as pd
from datetime import date, timedelta, datetime
from pathlib import Path
from tqdm import tqdm  # notebookではなく通常版
import warnings
from dotenv import load_dotenv  # .envファイルから読み込む

# urllib3のInsecureRequestWarningを非表示にする
warnings.filterwarnings('ignore', category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

# .envファイルの読み込み（プロジェクトフォルダに配置しておく）
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

# --- 設定項目 ---
class Config:
    """EDINETデータ取得用の設定クラス"""
    # アクセス設定
    API_BASE_URL = "https://disclosure.edinet-fsa.go.jp/api/v2"
    REQUEST_TIMEOUT = 30
    DOWNLOAD_TIMEOUT = 60

    # 基本パス（環境変数が未設定ならデフォルト値を使用）
    BASE_DIR = Path(os.getenv("EDINET_BASE_DIR", "C:/Users/0602JP/Documents/EDINET_DB/"))
    # ダウンロードしたZIPファイルの保存先
    SAVE_FOLDER = BASE_DIR / "01_zip_files/"
    # ダウンロード失敗ログの保存先
    FAILED_LOG_PATH = BASE_DIR / "failed_downloads.csv"

    # SQLiteデータベースファイルのパス
    DB_PATH = BASE_DIR / "edinet_data.db"
    
    # CSV一時抽出フォルダのパス (SQLite格納後、削除を検討)
    EXTRACTED_CSV_TEMP_FOLDER = BASE_DIR / "02_extracted_csv_temp/"

    # APIキーの取得とチェック
    API_KEY = os.getenv("EDINET_API_KEY")
    if not API_KEY:
        raise ValueError("EDINET_API_KEY が .env に設定されていません。")

    # データ取得設定
    # データの信頼性を担保するため、何日分遡ってデータを再取得するか
    RELIABILITY_DAYS = 7
    # 初回実行時に何年分のデータを取得するか
    INITIAL_FETCH_YEARS = 1

    # ダウンロード対象の書類タイプコード
    # 120: 有価証券報告書, 140: 四半期報告書, 160: 半期報告書
    TARGET_DOC_TYPE_CODES = ['120', '140', '160']