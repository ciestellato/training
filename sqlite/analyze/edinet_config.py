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
    """設定を管理するクラス"""
    # ローカル環境の基本パス（任意の保存先に変更してください）
    BASE_DIR = Path("C:/Users/0602JP/Documents/EDINET_DB/")
    # ダウンロードしたZIPファイルの保存先
    SAVE_FOLDER = BASE_DIR / "01_zip_files/"

    # .envファイルからAPIキーを取得
    API_KEY = os.getenv("EDINET_API_KEY")

    # データの信頼性を担保するため、何日分遡ってデータを再取得するか
    RELIABILITY_DAYS = 7
    # 初回実行時に何年分のデータを取得するか
    INITIAL_FETCH_YEARS = 5

    # ダウンロード対象の書類タイプコード
    # 120: 有価証券報告書, 140: 四半期報告書, 160: 半期報告書
    TARGET_DOC_TYPE_CODES = ['120', '140', '160']