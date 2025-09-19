# EDINET APIで自分だけのデータベースを作成したい！<!-- omit in toc -->

- [参考URL](#参考url)
- [作業ログ](#作業ログ)
  - [EDINET API接続完了 (2025-09-17)](#edinet-api接続完了-2025-09-17)
    - [1. APIキーの発行](#1-apiキーの発行)
    - [2. EDINET APIで情報を取得する](#2-edinet-apiで情報を取得する)
      - [環境構築](#環境構築)
      - [コード](#コード)
        - [edinet\_config.py](#edinet_configpy)
        - [edinet\_steps.py](#edinet_stepspy)
        - [edinet\_main.py](#edinet_mainpy)
      - [結果](#結果)
  - [進捗ログのCSV出力(2025-09-18)](#進捗ログのcsv出力2025-09-18)
  - [ダウンロード失敗のリカバリー(2025-09-18)](#ダウンロード失敗のリカバリー2025-09-18)
  - [Zipの中身確認(2025-09-18)](#zipの中身確認2025-09-18)
  - [SQLiteの保存](#sqliteの保存)
  - [毎回テーブルの削除＆新規作成を修正](#毎回テーブルの削除新規作成を修正)

## 参考URL

1. [金融庁 EDINET 閲覧サイト](https://disclosure2.edinet-fsa.go.jp/week0010.aspx)
2. [[EDINET] 上場企業の業績データをAPIで取得する](https://qiita.com/hifistar/items/0114c6f60ded96785178)
3. [【Python×EDINET API】CSVで財務データを自動取得！差分更新で構築する金融分析データベース](https://qiita.com/invest-aitech/items/7e13e89821bd754dfc25)


## 作業ログ

### EDINET API接続完了 (2025-09-17)

#### 1. APIキーの発行

必要事項を入力して、APIキーを発行する。

[EDINET API v2 仕様書](https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/download/ESE140206.pdf)

> 2-3-1 アカウントの作成について 
> 
> EDINET API のアカウント作成について説明します。
>  
> 2-3-1-1 サインイン画面の表示 
> 
> アカウントを作成する場合は、次のURLにアクセスし、サインイン画面を表示します。 
> 
> https://api.edinet-fsa.go.jp/api/auth/index.aspx?mode=1

※ポップアップブロックを解除していないとAPIキーが表示されないので注意

#### 2. EDINET APIで情報を取得する

参考URL3のQiitaの記事はGoogle ColaboratoryとGoogle Driveだったため、まずはローカル環境で実行できるようにしていく。

##### 環境構築

インストールしたもの(すべてpipインストール)

- requests
- pandas
- tqdm

`.env`ファイルにAPIキーを保存しておく

##### コード

Copilotに相談して、ローカルで実行できるようにした。

###### edinet_config.py

```
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
```

###### edinet_steps.py

```
import os
import time
import requests
import pandas as pd
from datetime import date, timedelta
from pathlib import Path
from tqdm import tqdm
import warnings
from edinet_config import Config
import logging
import traceback

# urllib3のInsecureRequestWarningを非表示にする
warnings.filterwarnings('ignore', category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

def update_summary_file(base_dir: Path, api_key: str) -> pd.DataFrame:
    """EDINETから日次の書類一覧を取得し、サマリーファイルを更新する。"""
    summary_path = base_dir / "EDINET_Summary_v3.csv"
    logging.info(f"サマリーファイル '{summary_path.name}' の状態を確認・更新します...")

    today = date.today()
    summary = pd.DataFrame()
    start_day = today - timedelta(days=365 * Config.INITIAL_FETCH_YEARS)

    if summary_path.exists():
        try:
            dtype_map = {'secCode': str, 'docTypeCode': str, 'xbrlFlag': str, 'csvFlag': str}
            summary = pd.read_csv(summary_path, encoding='utf_8_sig', dtype=dtype_map)
            summary['submitDateTime'] = pd.to_datetime(summary['submitDateTime'], errors='coerce')

            if not summary.empty and 'submitDateTime' in summary.columns and not summary['submitDateTime'].isnull().all():
                latest_date_in_file = summary['submitDateTime'].max().date()
                start_day = latest_date_in_file - timedelta(days=Config.RELIABILITY_DAYS)
        except Exception as e:
            logging.warning(f"サマリーファイルの読み込み中にエラーが発生しました: {e}")
            logging.debug(traceback.format_exc())

    end_day = today
    day_term = [start_day + timedelta(days=i) for i in range((end_day - start_day).days + 1)]

    new_docs = []
    for day in tqdm(day_term, desc="APIからメタデータ取得"):
        params = {'date': day.strftime('%Y-%m-%d'), 'type': 2, 'Subscription-Key': api_key}
        try:
            response = requests.get(
                Config.API_BASE_URL + "/documents.json",
                params=params,
                verify=False,
                timeout=Config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            res_json = response.json()
            if res_json.get('results'):
                new_docs.extend(res_json['results'])
        except requests.exceptions.RequestException as e:
            logging.warning(f"エラー: {day} のデータ取得に失敗 - {e}")
            logging.debug(traceback.format_exc())
        time.sleep(0.1)

    if new_docs:
        temp_df = pd.DataFrame(new_docs)
        summary = pd.concat([summary, temp_df], ignore_index=True)

    summary['submitDateTime'] = pd.to_datetime(summary['submitDateTime'], errors='coerce')
    summary.dropna(subset=['docID'], inplace=True)
    summary = summary.drop_duplicates(subset='docID', keep='last')
    summary = summary.sort_values(by='submitDateTime', ascending=True).reset_index(drop=True)
    try:
        summary.to_csv(summary_path, index=False, encoding='utf_8_sig')
        logging.info("✅ サマリーファイルの更新が完了しました！")
    except Exception as e:
        logging.error(f"サマリーファイルの保存に失敗しました: {e}")
        logging.debug(traceback.format_exc())
    return summary

def step1_create_and_summarize():
    """ステップ①: サマリーを作成し、その概要を出力する。"""
    logging.info("--- ステップ① サマリー作成と概要の表示 ---")
    summary_df = update_summary_file(Config.BASE_DIR, Config.API_KEY)

    if summary_df.empty:
        logging.warning("⚠️ サマリーデータの作成に失敗したか、データがありませんでした。")
        return pd.DataFrame()

    logging.info(f"  - データ期間: {summary_df['submitDateTime'].min():%Y-%m-%d} ～ {summary_df['submitDateTime'].max():%Y-%m-%d}")
    logging.info(f"  - 総データ数: {len(summary_df)} 件")
    logging.info(f"  - 銘柄数（ユニーク）: {summary_df['secCode'].nunique()} 社")
    logging.info("-" * 40)

    return summary_df

def step2_check_download_status(summary_df: pd.DataFrame):
    """
    ステップ②: ダウンロードフォルダの状況を確認し、未ダウンロードの件数などを出力する。
    """
    logging.info("--- ステップ② ダウンロード状況の確認 ---")
    save_folder = Config.SAVE_FOLDER
    save_folder.mkdir(parents=True, exist_ok=True)

    # サブフォルダ内も含めて、既存の全zipファイルを再帰的に検索
    existing_files_path = list(save_folder.rglob('*.zip'))

    logging.info(f"📁 指定フォルダ: {save_folder}")
    if not existing_files_path:
        logging.info("  - 既存のダウンロード済みファイルはありません。")
    else:
        logging.info(f"  - 既存ファイル数: {len(existing_files_path)} 件")

    # --- ▼▼▼ ダウンロード対象の条件を定義 ▼▼▼ ---
    query_str = (
        "csvFlag == '1' and "
        "secCode.notna() and secCode != 'None' and "
        f"docTypeCode in {Config.TARGET_DOC_TYPE_CODES}"
    )
    target_docs = summary_df.query(query_str)
    # --- ▲▲▲ ダウンロード対象の条件を定義 ▲▲▲ ---

    # 既存ファイル名（docID）のセットを作成
    existing_file_stems = {f.stem for f in existing_files_path}

    # ダウンロード対象のうち、まだダウンロードされていないものを抽出
    docs_to_download = target_docs[~target_docs['docID'].isin(existing_file_stems)]

    logging.info("\n📊 サマリーと照合した結果:")
    logging.info(f"  - ダウンロード対象の総書類数（CSV提供あり）: {len(target_docs)} 件")
    logging.info(f"  - ダウンロードが必要な（未取得の）書類数: {len(docs_to_download)} 件")
    logging.info("-" * 40)

    return docs_to_download

def step3_execute_download(docs_to_download: pd.DataFrame):
    """
    ステップ③: 実際にファイルのダウンロードを実行し、年/四半期フォルダに保存する。
    """
    logging.info("--- ステップ③ ダウンロードの実行 ---")
    if docs_to_download.empty:
        logging.info("✅ ダウンロード対象の新しいファイルはありません。処理を完了します。")
        logging.info("-" * 40)
        return

    logging.info(f"{len(docs_to_download)}件のファイルのダウンロードを開始します。")

    for _, row in tqdm(docs_to_download.iterrows(), total=len(docs_to_download), desc="ZIPダウンロード進捗"):
        doc_id = row['docID']
        submit_date = row['submitDateTime']

        # --- ファイル整理のロジック ---
        if pd.isna(submit_date):
            target_folder = Config.SAVE_FOLDER / "unknown_date"
        else:
            year = submit_date.year
            quarter = (submit_date.month - 1) // 3 + 1
            target_folder = Config.SAVE_FOLDER / str(year) / f"Q{quarter}"

        target_folder.mkdir(parents=True, exist_ok=True)
        zip_path = target_folder / f"{doc_id}.zip"

        # EDINET API のファイル取得エンドポイント
        url_zip = f"{Config.API_BASE_URL}/documents/{doc_id}"
        params_zip = {"type": 5, 'Subscription-Key': Config.API_KEY}

        try:
            r = requests.get(url_zip, params=params_zip, stream=True, verify=False, timeout=Config.DOWNLOAD_TIMEOUT)
            r.raise_for_status()
            with open(zip_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        except requests.exceptions.RequestException as e:
            logging.warning(f"ダウンロード失敗: {doc_id}, エラー: {e}")
            logging.debug(traceback.format_exc())
            if zip_path.exists():
                zip_path.unlink()
        time.sleep(0.1)

    logging.info("✅ ダウンロード処理が完了しました。")
    logging.info("-" * 40)
```

###### edinet_main.py

```
from edinet_steps import (
    step1_create_and_summarize,
    step2_check_download_status,
    step3_execute_download
)
import logging
import traceback
from edinet_config import Config
from pathlib import Path

# ログファイルの保存先を指定
log_path = Config.BASE_DIR / "edinet_log.txt"

# ログ設定：INFO以上を表示、ファイルとコンソール両方に出力
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(log_path, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def main() -> bool:
    """EDINETデータの取得とダウンロード処理"""
    try:
        logging.info("処理を開始します。")

        summary_data = step1_create_and_summarize()

        if summary_data.empty:
            logging.warning("サマリーデータが空です。ダウンロード処理はスキップされます。")
            return False

        files_to_download = step2_check_download_status(summary_data)

        if files_to_download.empty:
            logging.info("新規ダウンロード対象はありません。")
        else:
            step3_execute_download(files_to_download)

        logging.info("全ての処理が完了しました。🎉")
        return True

    except Exception as e:
        logging.error(f"エラーが発生しました: {e}")
        logging.debug(traceback.format_exc())
        return False

if __name__ == '__main__':
    success = main()
    if not success:
        logging.warning("一部の処理が正常に完了しませんでした。")
```

##### 結果

zipファイルのダウンロードに成功した

### 進捗ログのCSV出力(2025-09-18)

ダウンロード履歴をCSVで出力するようにした。

```
def step3_execute_download(docs_to_download: pd.DataFrame):
    """
    ステップ③: 実際にファイルのダウンロードを実行し、年/四半期フォルダに保存する。
    """
    logging.info("--- ステップ③ ダウンロードの実行 ---")
    if docs_to_download.empty:
        logging.info("✅ ダウンロード対象の新しいファイルはありません。処理を完了します。")
        logging.info("-" * 40)
        return

    logging.info(f"{len(docs_to_download)}件のファイルのダウンロードを開始します。")
    log_records = []  # ログ記録用リスト

    for _, row in tqdm(docs_to_download.iterrows(), total=len(docs_to_download), desc="ZIPダウンロード進捗"):
        doc_id = row['docID']
        submit_date = row['submitDateTime']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # --- ファイル整理のロジック ---
        if pd.isna(submit_date):
            target_folder = Config.SAVE_FOLDER / "unknown_date"
        else:
            year = submit_date.year
            quarter = (submit_date.month - 1) // 3 + 1
            target_folder = Config.SAVE_FOLDER / str(year) / f"Q{quarter}"

        target_folder.mkdir(parents=True, exist_ok=True)
        zip_path = target_folder / f"{doc_id}.zip"

        # EDINET API のファイル取得エンドポイント
        url_zip = f"{Config.API_BASE_URL}/documents/{doc_id}"
        params_zip = {"type": 5, 'Subscription-Key': Config.API_KEY}

        try:
            r = requests.get(url_zip, params=params_zip, stream=True, verify=False, timeout=Config.DOWNLOAD_TIMEOUT)
            r.raise_for_status()
            with open(zip_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            status = "success"
            error_msg = ""
        except requests.exceptions.RequestException as e:
            logging.warning(f"ダウンロード失敗: {doc_id}, エラー: {e}")
            logging.debug(traceback.format_exc())
            if zip_path.exists():
                zip_path.unlink()
            status = "failed"
            error_msg = str(e)

        log_records.append({
            "docID": doc_id,
            "submitDateTime": submit_date,
            "status": status,
            "errorMessage": error_msg,
            "savedPath": str(zip_path if status == "success" else ""),
            "timestamp": timestamp
        })

        time.sleep(0.1)
        
    # CSVに保存
    log_df = pd.DataFrame(log_records)
    log_csv_path = Config.BASE_DIR / "download_log.csv"
    try:
        log_df.to_csv(log_csv_path, index=False, encoding='utf_8_sig')
        logging.info(f"📄 ダウンロードログを保存しました: {log_csv_path}")
    except Exception as e:
        logging.error(f"ログCSVの保存に失敗しました: {e}")
        logging.debug(traceback.format_exc())

    logging.info("✅ ダウンロード処理が完了しました。")
    logging.info("-" * 40)
```

### ダウンロード失敗のリカバリー(2025-09-18)

ダウンロードに失敗したファイルのみを記録して、再ダウンロードできる仕組みを作りたい

- 成功ファイルの記録廃止
- 失敗ファイルのみ記録
- 失敗履歴からの再ダウンロード
- 再ダウンロード成功したら失敗履歴から削除
- mainメソッド
  - 前回の失敗のリトライ
  - 今回の処理
  - 今回の失敗のリトライ

```
from edinet_steps import (
    step1_create_and_summarize,
    step2_check_download_status,
    step3_execute_download,
    retry_failed_downloads
)
import logging
import traceback
from edinet_config import Config
from pathlib import Path

# ログファイルの保存先を指定
log_path = Config.BASE_DIR / "edinet_log.txt"

# ログ設定：INFO以上を表示、ファイルとコンソール両方に出力
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(log_path, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def main() -> bool:
    """EDINETデータの取得とダウンロード処理"""
    try:
        logging.info("処理を開始します。")

        # 🔁 Step 0: 前回の失敗ファイルを再試行

        logging.info("🔁 Step 0: 前回の失敗ファイルを再試行します。")
        retry_failed_downloads()

        # 🧾 Step 1: サマリー作成

        summary_data = step1_create_and_summarize()
        if summary_data.empty:
            logging.warning("サマリーデータが空です。ダウンロード処理はスキップされます。")
            return False

        # 📋 Step 2: ダウンロード対象の抽出

        files_to_download = step2_check_download_status(summary_data)

        # 📦 Step 3: ダウンロード実行

        if files_to_download.empty:
            logging.info("新規ダウンロード対象はありません。")
        else:
            step3_execute_download(files_to_download)

        # 🔁 Step 4: 今回の失敗ファイルを再試行
        
        logging.info("🔁 Step 4: 今回の失敗ファイルを再試行します。")
        retry_failed_downloads()

        logging.info("全ての処理が完了しました。🎉")
        return True

    except Exception as e:
        logging.error(f"エラーが発生しました: {e}")
        logging.debug(traceback.format_exc())
        return False

if __name__ == '__main__':
    success = main()
    if not success:
        logging.warning("一部の処理が正常に完了しませんでした。")
```

```
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
```

```
import os
import time
import requests
import pandas as pd
from datetime import date, timedelta, datetime
from pathlib import Path
from tqdm import tqdm
import warnings
from edinet_config import Config
import logging
import traceback

# urllib3のInsecureRequestWarningを非表示にする
warnings.filterwarnings('ignore', category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

def update_summary_file(base_dir: Path, api_key: str) -> pd.DataFrame:
    """EDINETから日次の書類一覧を取得し、サマリーファイルを更新する。"""
    summary_path = base_dir / "EDINET_Summary_v3.csv"
    logging.info(f"サマリーファイル '{summary_path.name}' の状態を確認・更新します...")

    today = date.today()
    summary = pd.DataFrame()
    start_day = today - timedelta(days=365 * Config.INITIAL_FETCH_YEARS)

    if summary_path.exists():
        try:
            dtype_map = {'secCode': str, 'docTypeCode': str, 'xbrlFlag': str, 'csvFlag': str}
            summary = pd.read_csv(summary_path, encoding='utf_8_sig', dtype=dtype_map)
            summary['submitDateTime'] = pd.to_datetime(summary['submitDateTime'], errors='coerce')

            if not summary.empty and 'submitDateTime' in summary.columns and not summary['submitDateTime'].isnull().all():
                latest_date_in_file = summary['submitDateTime'].max().date()
                start_day = latest_date_in_file - timedelta(days=Config.RELIABILITY_DAYS)
        except Exception as e:
            logging.warning(f"サマリーファイルの読み込み中にエラーが発生しました: {e}")
            logging.debug(traceback.format_exc())

    end_day = today
    day_term = [start_day + timedelta(days=i) for i in range((end_day - start_day).days + 1)]

    new_docs = []
    for day in tqdm(day_term, desc="APIからメタデータ取得"):
        params = {'date': day.strftime('%Y-%m-%d'), 'type': 2, 'Subscription-Key': api_key}
        try:
            response = requests.get(
                Config.API_BASE_URL + "/documents.json",
                params=params,
                verify=False,
                timeout=Config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            res_json = response.json()
            if res_json.get('results'):
                new_docs.extend(res_json['results'])
        except requests.exceptions.RequestException as e:
            logging.warning(f"エラー: {day} のデータ取得に失敗 - {e}")
            logging.debug(traceback.format_exc())
        time.sleep(0.1)

    if new_docs:
        temp_df = pd.DataFrame(new_docs)
        summary = pd.concat([summary, temp_df], ignore_index=True)

    summary['submitDateTime'] = pd.to_datetime(summary['submitDateTime'], errors='coerce')
    summary.dropna(subset=['docID'], inplace=True)
    summary = summary.drop_duplicates(subset='docID', keep='last')
    summary = summary.sort_values(by='submitDateTime', ascending=True).reset_index(drop=True)
    try:
        summary.to_csv(summary_path, index=False, encoding='utf_8_sig')
        logging.info("✅ サマリーファイルの更新が完了しました！")
    except Exception as e:
        logging.error(f"サマリーファイルの保存に失敗しました: {e}")
        logging.debug(traceback.format_exc())
    return summary

def step1_create_and_summarize():
    """ステップ①: サマリーを作成し、その概要を出力する。"""
    logging.info("--- ステップ① サマリー作成と概要の表示 ---")
    summary_df = update_summary_file(Config.BASE_DIR, Config.API_KEY)

    if summary_df.empty:
        logging.warning("⚠️ サマリーデータの作成に失敗したか、データがありませんでした。")
        return pd.DataFrame()

    logging.info(f"  - データ期間: {summary_df['submitDateTime'].min():%Y-%m-%d} ～ {summary_df['submitDateTime'].max():%Y-%m-%d}")
    logging.info(f"  - 総データ数: {len(summary_df)} 件")
    logging.info(f"  - 銘柄数（ユニーク）: {summary_df['secCode'].nunique()} 社")
    logging.info("-" * 40)

    return summary_df

def step2_check_download_status(summary_df: pd.DataFrame):
    """
    ステップ②: ダウンロードフォルダの状況を確認し、未ダウンロードの件数などを出力する。
    """
    logging.info("--- ステップ② ダウンロード状況の確認 ---")
    save_folder = Config.SAVE_FOLDER
    save_folder.mkdir(parents=True, exist_ok=True)

    # サブフォルダ内も含めて、既存の全zipファイルを再帰的に検索
    existing_files_path = list(save_folder.rglob('*.zip'))

    logging.info(f"📁 指定フォルダ: {save_folder}")
    if not existing_files_path:
        logging.info("  - 既存のダウンロード済みファイルはありません。")
    else:
        logging.info(f"  - 既存ファイル数: {len(existing_files_path)} 件")

    # --- ▼▼▼ ダウンロード対象の条件を定義 ▼▼▼ ---
    query_str = (
        "csvFlag == '1' and "
        "secCode.notna() and secCode != 'None' and "
        f"docTypeCode in {Config.TARGET_DOC_TYPE_CODES}"
    )
    target_docs = summary_df.query(query_str)
    # --- ▲▲▲ ダウンロード対象の条件を定義 ▲▲▲ ---

    # 既存ファイル名（docID）のセットを作成
    existing_file_stems = {f.stem for f in existing_files_path}

    # ダウンロード対象のうち、まだダウンロードされていないものを抽出
    docs_to_download = target_docs[~target_docs['docID'].isin(existing_file_stems)]

    logging.info("\n📊 サマリーと照合した結果:")
    logging.info(f"  - ダウンロード対象の総書類数（CSV提供あり）: {len(target_docs)} 件")
    logging.info(f"  - ダウンロードが必要な（未取得の）書類数: {len(docs_to_download)} 件")
    logging.info("-" * 40)

    return docs_to_download

def download_single_file(doc_id: str, submit_date, save_folder: Path) -> bool:
    """1件のEDINETファイルをダウンロードし、保存。成功ならTrue、失敗ならFalse"""
    if pd.isna(submit_date):
        target_folder = save_folder / "unknown_date"
    else:
        year = submit_date.year
        quarter = (submit_date.month - 1) // 3 + 1
        target_folder = save_folder / str(year) / f"Q{quarter}"

    target_folder.mkdir(parents=True, exist_ok=True)
    zip_path = target_folder / f"{doc_id}.zip"

    # EDINET API のファイル取得エンドポイント
    url_zip = f"{Config.API_BASE_URL}/documents/{doc_id}"
    params_zip = {"type": 5, 'Subscription-Key': Config.API_KEY}

    try:
        r = requests.get(url_zip, params=params_zip, stream=True, verify=False, timeout=Config.DOWNLOAD_TIMEOUT)
        r.raise_for_status()
        with open(zip_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except requests.exceptions.RequestException as e:
        logging.warning(f"ダウンロード失敗: {doc_id}, エラー: {e}")
        logging.debug(traceback.format_exc())
        if zip_path.exists():
            zip_path.unlink()
        return False

def log_failed_download(doc_id, submit_date, error_msg):
    """ステップ3でダウンロードに失敗したファイルを記録する"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    failed_record = pd.DataFrame([{
        "docID": doc_id,
        "submitDateTime": submit_date,
        "errorMessage": error_msg,
        "timestamp": timestamp
    }])
    failed_log_path = Config.FAILED_LOG_PATH
    failed_record.to_csv(failed_log_path, mode='a', header=not failed_log_path.exists(), index=False, encoding='utf_8_sig')

def step3_execute_download(docs_to_download: pd.DataFrame):
    """
    ステップ③: 実際にファイルのダウンロードを実行し、年/四半期フォルダに保存する。
    """
    logging.info("--- ステップ③ ダウンロードの実行 ---")
    if docs_to_download.empty:
        logging.info("✅ ダウンロード対象の新しいファイルはありません。処理を完了します。")
        logging.info("-" * 40)
        return

    logging.info(f"{len(docs_to_download)}件のファイルのダウンロードを開始します。")

    for _, row in tqdm(docs_to_download.iterrows(), total=len(docs_to_download), desc="ZIPダウンロード進捗"):
        doc_id = row['docID']
        submit_date = row['submitDateTime']
        
        # --- ファイル整理のロジック ---
        success = download_single_file(doc_id, submit_date, Config.SAVE_FOLDER)
        if not success:
            log_failed_download(doc_id, submit_date, "初回ダウンロード失敗")

        time.sleep(0.1)

    logging.info("✅ ダウンロード処理が完了しました。")
    logging.info("-" * 40)

def retry_failed_downloads():
    """失敗したダウンロードを再試行し、成功したものはログから削除する"""
    failed_log_path = Config.FAILED_LOG_PATH

    if not failed_log_path.exists():
        logging.info("再試行対象の失敗ログは存在しません。")
        return

    try:
        failed_df = pd.read_csv(failed_log_path, encoding='utf_8_sig')
    except Exception as e:
        logging.error(f"失敗ログの読み込みに失敗しました: {e}")
        logging.debug(traceback.format_exc())
        return

    if failed_df.empty:
        logging.info("失敗ログは空です。")
        return

    logging.info(f"🔁 {len(failed_df)} 件の失敗ファイルを再試行します。")
    successful_ids = []
    failed_again = [] # 再失敗記録用

    for _, row in tqdm(failed_df.iterrows(), total=len(failed_df), desc="再試行中"):
        doc_id = row['docID']
        submit_date = pd.to_datetime(row['submitDateTime'], errors='coerce')

        success = download_single_file(doc_id, submit_date, Config.SAVE_FOLDER)

        if success:
            successful_ids.append(doc_id)
        else:
            logging.warning(f"再試行失敗: {doc_id}")
            failed_again.append((doc_id, submit_date))

        time.sleep(0.1)
        
    # 成功したIDをログから削除
    remaining_df = failed_df[~failed_df['docID'].isin(successful_ids)]
    remaining_df.to_csv(failed_log_path, index=False, encoding='utf_8_sig')

    # 再記録（失敗したものだけ）
    for doc_id, submit_date in failed_again:
        log_failed_download(doc_id, submit_date, "再試行失敗")

    logging.info(f"✅ 再試行完了。成功: {len(successful_ids)} 件 / 残り: {len(remaining_df) + len(failed_again)} 件")
```

### Zipの中身確認(2025-09-18)

zip_utils.py

```
from pathlib import Path
import zipfile
import logging

def inspect_zip_contents(zip_path: Path) -> list[str]:
    """
    指定されたZIPファイルの中身（ファイル名一覧）を返す。
    """
    if not zip_path.exists():
        logging.warning(f"ZIPファイルが存在しません: {zip_path}")
        return []

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            logging.info(f"{zip_path.name} の内容:")
            for f in file_list:
                logging.info(f"  - {f}")
            return file_list
    except zipfile.BadZipFile:
        logging.error(f"ZIPファイルが壊れている可能性があります: {zip_path}")
        return []

def extract_xbrl_from_zip(zip_path: Path, extract_to: Path) -> list[Path]:
    """
    ZIPファイルからXBRLファイルを抽出し、指定フォルダに保存。
    抽出されたファイルのパス一覧を返す。
    """
    extracted_files = []
    if not zip_path.exists():
        logging.warning(f"ZIPファイルが存在しません: {zip_path}")
        return []

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for file_name in zip_ref.namelist():
                if file_name.lower().endswith(".xbrl"):
                    zip_ref.extract(file_name, path=extract_to)
                    extracted_files.append(extract_to / file_name)
        logging.info(f"{len(extracted_files)} 件のXBRLファイルを抽出しました。")
        return extracted_files
    except zipfile.BadZipFile:
        logging.error(f"ZIPファイルが壊れている可能性があります: {zip_path}")
        return []
```

test_zip_utils.py

```
import pytest
from pathlib import Path
from zip_utils import inspect_zip_contents, extract_xbrl_from_zip
import zipfile

@pytest.fixture
def sample_zip(tmp_path):
    """一時的なZIPファイルを作成して返す"""
    zip_path = tmp_path / "test_sample.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.writestr("XBRL/PublicDoc/sample.xbrl", "<xbrl>...</xbrl>")
        zipf.writestr("README.txt", "This is a test file.")
    return zip_path

def test_inspect_zip_contents_valid(sample_zip):
    """正常なZIPファイルの中身を確認"""
    contents = inspect_zip_contents(sample_zip)
    assert "XBRL/PublicDoc/sample.xbrl" in contents
    assert "README.txt" in contents
    assert len(contents) == 2

def test_inspect_zip_contents_missing():
    """存在しないZIPファイルを指定した場合"""
    fake_path = Path("non_existent.zip")
    contents = inspect_zip_contents(fake_path)
    assert contents == []

def test_inspect_zip_contents_corrupt(tmp_path):
    """壊れたZIPファイルを指定した場合"""
    corrupt_zip = tmp_path / "corrupt.zip"
    corrupt_zip.write_text("これはZIPではありません")
    contents = inspect_zip_contents(corrupt_zip)
    assert contents == []

def test_extract_xbrl_from_zip_valid(sample_zip, tmp_path):
    """正常なZIPからXBRLファイルを抽出できるか"""
    extract_dir = tmp_path / "extracted"
    extracted_files = extract_xbrl_from_zip(sample_zip, extract_dir)

    assert len(extracted_files) == 1
    assert extracted_files[0].name == "sample.xbrl"
    assert extracted_files[0].exists()
    assert extracted_files[0].read_text().startswith("<xbrl>")

def test_extract_xbrl_from_zip_no_xbrl(tmp_path):
    """XBRLファイルが含まれていないZIPの処理"""
    zip_path = tmp_path / "no_xbrl.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.writestr("README.txt", "No XBRL here.")
    extract_dir = tmp_path / "extracted"
    extracted_files = extract_xbrl_from_zip(zip_path, extract_dir)

    assert extracted_files == []

def test_extract_xbrl_from_zip_corrupt(tmp_path):
    """壊れたZIPファイルの処理"""
    corrupt_zip = tmp_path / "corrupt.zip"
    corrupt_zip.write_text("Not a zip file")
    extract_dir = tmp_path / "extracted"
    extracted_files = extract_xbrl_from_zip(corrupt_zip, extract_dir)

    assert extracted_files == []
```

check_zip.py

```
from pathlib import Path
import zipfile

def preview_zip_contents(zip_path: Path, max_files: int = 50):
    """ZIPファイルの中身を表示する"""
    if not zip_path.exists():
        print(f"❌ ファイルが見つかりません: {zip_path}")
        return

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            print(f"📦 ZIPファイル: {zip_path.name}")
            print(f"📁 含まれるファイル数: {len(file_list)}")
            print("🔍 ファイル一覧:")
            for i, f in enumerate(file_list):
                if i >= max_files:
                    print("...（省略）")
                    break
                print(f"  - {f}")
    except zipfile.BadZipFile:
        print(f"⚠️ ZIPファイルが壊れている可能性があります: {zip_path}")

def extract_csv_from_zip(zip_path: str, extract_to: str = "./extracted_csv"):
    """ZIPファイルからCSVファイルのみを抽出する"""
    zip_path = Path(zip_path)
    extract_to = Path(extract_to)
    extract_to.mkdir(parents=True, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            csv_files = [f for f in zip_ref.namelist() if f.endswith('.csv')]
            zip_ref.extractall(path=extract_to, members=csv_files)
            return [str(extract_to / f) for f in csv_files]
    except zipfile.BadZipFile:
        print(f"⚠️ ZIPファイルが壊れている可能性があります: {zip_path}")
        return []
```

test_check_zip.py

```
import pytest
from pathlib import Path
from edinet_config import Config
from check_zip import extract_csv_from_zip

def get_latest_zip_file() -> Path:
    zip_files = sorted(Config.SAVE_FOLDER.rglob("*.zip"))
    if not zip_files:
        raise FileNotFoundError(f"No ZIP files found in {Config.SAVE_FOLDER}")
    return zip_files[-1]

def test_extract_csv_from_zip():
    zip_path = get_latest_zip_file()
    extract_to = Path("./test_output")
    extract_to.mkdir(exist_ok=True)

    extracted_files = extract_csv_from_zip(str(zip_path), extract_to=str(extract_to))

    assert len(extracted_files) > 0, "CSVファイルが抽出されませんでした"
    for file in extracted_files:
        assert file.endswith(".csv")
        print(f"✅ 抽出されたCSV: {file}")
```

### SQLiteの保存

edinet_main.py

```
from edinet_steps import (
    step1_create_and_summarize,
    step2_check_download_status,
    step3_execute_download,
    retry_failed_downloads,
    step_store_summary_to_db,
    step_extract_and_index_csv 
)
import logging
import traceback
from edinet_config import Config
from pathlib import Path

# ログファイルの保存先を指定
log_path = Config.BASE_DIR / "edinet_log.txt"

# ログ設定：INFO以上を表示、ファイルとコンソール両方に出力
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(log_path, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def main() -> bool:
    """EDINETデータの取得とダウンロード処理"""
    try:
        logging.info("処理を開始します。")

        # 🔁 Step 0: 前回の失敗ファイルを再試行

        logging.info("🔁 Step 0: 前回の失敗ファイルを再試行します。")
        retry_failed_downloads()

        # 🧾 Step 1: サマリー作成

        summary_data = step1_create_and_summarize()
        if summary_data.empty:
            logging.warning("サマリーデータが空です。ダウンロード処理はスキップされます。")
            return False

        # 📋 Step 2: ダウンロード対象の抽出

        files_to_download = step2_check_download_status(summary_data)

        # 📦 Step 3: ダウンロード実行

        if files_to_download.empty:
            logging.info("新規ダウンロード対象はありません。")
        else:
            step3_execute_download(files_to_download)

        # 🔁 Step 4: 今回の失敗ファイルを再試行

        logging.info("🔁 Step 4: 今回の失敗ファイルを再試行します。")
        retry_failed_downloads()

        # 📊 Step 5: サマリーデータをSQLiteに保管
        step_store_summary_to_db(summary_data)

        # 📄 Step 6: ダウンロード済みZIPからCSVを抽出し、パスをSQLiteに記録
        step_extract_and_index_csv(Config.SAVE_FOLDER)

        logging.info("全ての処理が完了しました。🎉")
        return True

    except Exception as e:
        logging.error(f"エラーが発生しました: {e}")
        logging.debug(traceback.format_exc())
        return False

if __name__ == '__main__':
    success = main()
    if not success:
        logging.warning("一部の処理が正常に完了しませんでした。")
```

edinet_config.py

```
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
```

edinet_steps.py

```
import os
import time
import requests
import pandas as pd
from datetime import date, timedelta, datetime
from pathlib import Path
from tqdm import tqdm
import warnings
from edinet_config import Config
import logging
import traceback
import sqlite3 # SQLiteをインポート

# zip_utilsからCSV抽出関数をインポート
from zip_utils import extract_csv_from_zip 

# urllib3のInsecureRequestWarningを非表示にする
warnings.filterwarnings('ignore', category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

def update_summary_file(base_dir: Path, api_key: str) -> pd.DataFrame:
    """EDINETから日次の書類一覧を取得し、サマリーファイルを更新する。"""
    summary_path = base_dir / "EDINET_Summary_v3.csv"
    logging.info(f"サマリーファイル '{summary_path.name}' の状態を確認・更新します...")

    today = date.today()
    summary = pd.DataFrame()

    # Config.INITIAL_FETCH_YEARS から Config.RELIABILITY_DAYS を考慮して start_day を設定
    # 既存のサマリーファイルが存在しない場合は INITIAL_FETCH_YEARS 分遡る
    start_day = today - timedelta(days=365 * Config.INITIAL_FETCH_YEARS)

    if summary_path.exists():
        try:
            dtype_map = {'secCode': str, 'docTypeCode': str, 'xbrlFlag': str, 'csvFlag': str}
            summary = pd.read_csv(summary_path, encoding='utf_8_sig', dtype=dtype_map)
            summary['submitDateTime'] = pd.to_datetime(summary['submitDateTime'], errors='coerce')

            if not summary.empty and 'submitDateTime' in summary.columns and not summary['submitDateTime'].isnull().all():
                latest_date_in_file = summary['submitDateTime'].max().date()
                # 信頼性確保のため、最新日付からRELIABILITY_DAYS分遡って再取得開始
                start_day = latest_date_in_file - timedelta(days=Config.RELIABILITY_DAYS)
        except Exception as e:
            logging.warning(f"サマリーファイルの読み込み中にエラーが発生しました: {e}")
            logging.debug(traceback.format_exc())

    end_day = today
    day_term = [start_day + timedelta(days=i) for i in range((end_day - start_day).days + 1)]

    new_docs = []
    for day in tqdm(day_term, desc="APIからメタデータ取得"):
        # EDINET API仕様書 [32, 34] に基づくリクエストパラメータ
        params = {'date': day.strftime('%Y-%m-%d'), 'type': 2, 'Subscription-Key': api_key}
        try:
            response = requests.get(
                Config.API_BASE_URL + "/documents.json",
                params=params,
                verify=False, # 本番環境ではTrueを検討
                timeout=Config.REQUEST_TIMEOUT
            )
            # HTTPステータスコードが4xx/5xxの場合はここでRequestExceptionを発生させる
            # ただし、EDINET APIはエラー時もHTTP 200を返す場合があるため、JSONレスポンスの解析も必要 [1]
            response.raise_for_status()
            res_json = response.json()
            logging.debug(f"APIレスポンス (日: {day.strftime('%Y-%m-%d')}): {res_json}") # デバッグ用にレスポンス全体を出力

            status = None
            message = None

            # EDINET APIのエラーレスポンス構造を考慮してstatusとmessageを取得 [2, 3]
            if isinstance(res_json, dict):
                if 'metadata' in res_json and isinstance(res_json['metadata'], dict):
                    metadata = res_json['metadata']
                    status = metadata.get('status')
                    message = metadata.get('message')
                elif 'StatusCode' in res_json: # 401 Access denied の場合など [3]
                    status = res_json.get('StatusCode')
                    message = res_json.get('message')
            
            # ステータスコードに応じた処理 [1]
            if status == '404' or status == 404: 
                logging.info(f"情報なし: {day.strftime('%Y-%m-%d')} の書類一覧は見つかりませんでした。")
            elif status and (str(status) != '200'): # ステータスが200以外の場合
                log_msg = f"APIエラー: {day.strftime('%Y-%m-%d')} - Status: {status}, Message: {message if message else '詳細不明'}"
                logging.warning(log_msg)
            elif res_json.get('results'): # 正常レスポンスで'results'がある場合 [6]
                new_docs.extend(res_json['results'])
            elif status == '200' and not res_json.get('results'): # **👈 ここに新しい elif ブロックを追加します**
                # APIは正常応答 (status: 200, message: OK) だが、resultsが空の場合
                logging.info(f"情報なし: {day.strftime('%Y-%m-%d')} の提出書類はありませんでした。")
                logging.debug(f"APIレスポンス (日: {day.strftime('%Y-%m-%d')}): {res_json}") # デバッグ用にレスポンス全体を出力
            else: # その他の予期せぬレスポンスの場合 (これに入ることは稀になるはず)
                logging.warning(f"予期せぬAPIレスポンス形式またはデータなし: {day.strftime('%Y-%m-%d')}. レスポンス: {res_json}")

        except requests.exceptions.RequestException as e:
            # ネットワークエラーやHTTPステータスコードが4xx/5xxだった場合
            logging.warning(f"エラー: {day.strftime('%Y-%m-%d')} のデータ取得に失敗 (ネットワークまたはHTTPステータスエラー) - {e}")
            logging.debug(traceback.format_exc())
        except ValueError as e: # response.json()がJSONとしてパースできない場合
            logging.error(f"エラー: {day.strftime('%Y-%m-%d')} のAPIレスポンスがJSONとして解析できませんでした。エラー: {e}, レスポンス内容: {response.text[:500]}...")
            logging.debug(traceback.format_exc())
        except Exception as e: # その他の予期せぬエラー
            logging.error(f"エラー: {day.strftime('%Y-%m-%d')} のデータ取得中に予期せぬエラーが発生しました: {e}")
            logging.debug(traceback.format_exc())
        time.sleep(0.1) # APIへの負荷軽減のため
        
    if new_docs:
        temp_df = pd.DataFrame(new_docs)
        # 既存のサマリーデータと新しいデータを結合し、重複を排除
        # docIDは提出書類ごとに付与される一意の番号 [40, 102]
        summary = pd.concat([summary, temp_df], ignore_index=True) 
        summary['submitDateTime'] = pd.to_datetime(summary['submitDateTime'], errors='coerce')
        summary.dropna(subset=['docID'], inplace=True)
        summary = summary.drop_duplicates(subset='docID', keep='last')
        summary = summary.sort_values(by='submitDateTime', ascending=True).reset_index(drop=True)

        try:
            summary.to_csv(summary_path, index=False, encoding='utf_8_sig')
            logging.info("✅ サマリーファイルの更新が完了しました！")
        except Exception as e:
            logging.error(f"サマリーファイルの保存に失敗しました: {e}")
            logging.debug(traceback.format_exc())
    else:
        logging.info("新規に取得されたサマリーデータはありません。")

    return summary

def step1_create_and_summarize():
    """ステップ①: サマリーを作成し、その概要を出力する。"""
    logging.info("--- ステップ① サマリー作成と概要の表示 ---")
    summary_df = update_summary_file(Config.BASE_DIR, Config.API_KEY)

    if summary_df.empty:
        logging.warning("⚠️ サマリーデータの作成に失敗したか、データがありませんでした。")
        return pd.DataFrame()

    logging.info(f"  - データ期間: {summary_df['submitDateTime'].min():%Y-%m-%d} ～ {summary_df['submitDateTime'].max():%Y-%m-%d}")
    logging.info(f"  - 総データ数: {len(summary_df)} 件")
    logging.info(f"  - 銘柄数（ユニーク）: {summary_df['secCode'].nunique()} 社")
    logging.info("-" * 40)

    return summary_df

def step2_check_download_status(summary_df: pd.DataFrame):
    """
    ステップ②: ダウンロードフォルダの状況を確認し、未ダウンロードの件数などを出力する。
    """
    logging.info("--- ステップ② ダウンロード状況の確認 ---")
    save_folder = Config.SAVE_FOLDER
    save_folder.mkdir(parents=True, exist_ok=True)

    # サブフォルダ内も含めて、既存の全zipファイルを再帰的に検索
    existing_files_path = list(save_folder.rglob('*.zip'))

    logging.info(f"📁 指定フォルダ: {save_folder}")
    if not existing_files_path:
        logging.info("  - 既存のダウンロード済みファイルはありません。")
    else:
        logging.info(f"  - 既存ファイル数: {len(existing_files_path)} 件")

    # --- ▼▼▼ ダウンロード対象の条件を定義 ▼▼▼ ---
    query_str = (
        "csvFlag == '1' and " # CSV有無フラグが'1' [44]
        "secCode.notna() and secCode != 'None' and " # 証券コードが存在する
        f"docTypeCode in {Config.TARGET_DOC_TYPE_CODES}" # 対象書類タイプコード [107]
    )
    target_docs = summary_df.query(query_str)
    # --- ▲▲▲ ダウンロード対象の条件を定義 ▲▲▲ ---

    # 既存ファイル名（docID）のセットを作成
    existing_file_stems = {f.stem for f in existing_files_path}

    # ダウンロード対象のうち、まだダウンロードされていないものを抽出
    docs_to_download = target_docs[~target_docs['docID'].isin(existing_file_stems)]

    logging.info("📊 サマリーと照合した結果:")
    logging.info(f"  - ダウンロード対象の総書類数（CSV提供あり）: {len(target_docs)} 件")
    logging.info(f"  - ダウンロードが必要な（未取得の）書類数: {len(docs_to_download)} 件")
    logging.info("-" * 40)

    return docs_to_download

def download_single_file(doc_id: str, submit_date, save_folder: Path) -> bool:
    """1件のEDINETファイルをダウンロードし、保存。成功ならTrue、失敗ならFalse"""
    if pd.isna(submit_date):
        target_folder = save_folder / "unknown_date"
    else:
        year = submit_date.year
        quarter = (submit_date.month - 1) // 3 + 1
        target_folder = save_folder / str(year) / f"Q{quarter}"

    target_folder.mkdir(parents=True, exist_ok=True)
    zip_path = target_folder / f"{doc_id}.zip"

    # EDINET API のファイル取得エンドポイント [89]
    url_zip = f"{Config.API_BASE_URL}/documents/{doc_id}"
    # 必要書類タイプ '5' はCSV形式のZIPファイル [90, 93]
    params_zip = {"type": 5, 'Subscription-Key': Config.API_KEY}

    try:
        r = requests.get(url_zip, params=params_zip, stream=True, verify=False, timeout=Config.DOWNLOAD_TIMEOUT)
        r.raise_for_status()

        # Content-Typeをチェックして、ZIPファイルであることを確認 [92, 99]
        content_type = r.headers.get('Content-Type', '')
        if 'application/octet-stream' not in content_type: # ZIP形式の場合
            # エラーレスポンスがJSON形式で返ってくる可能性も考慮 [92]
            if 'application/json' in content_type:
                error_json = r.json()
                status = error_json.get('metadata', {}).get('status', 'N/A')
                message = error_json.get('metadata', {}).get('message', 'N/A')
                logging.warning(f"ダウンロード失敗: {doc_id}. APIがエラーJSONを返却。Status: {status}, Message: {message}")
            else:
                logging.warning(f"ダウンロード失敗: {doc_id}. 予期せぬContent-Type: {content_type}")
            if zip_path.exists():
                zip_path.unlink() # 不完全なファイルを削除
            return False

        with open(zip_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        return True

    except requests.exceptions.RequestException as e:
        logging.warning(f"ダウンロード失敗: {doc_id}, エラー: {e}")
        logging.debug(traceback.format_exc())
        if zip_path.exists():
            zip_path.unlink() # 失敗した場合はファイルを削除
        return False
    except Exception as e:
        logging.error(f"ファイル {doc_id} ダウンロード中に予期せぬエラー: {e}")
        logging.debug(traceback.format_exc())
        if zip_path.exists():
            zip_path.unlink()
        return False
    
def log_failed_download(doc_id, submit_date, error_msg):
    """ステップ3でダウンロードに失敗したファイルを記録する"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    failed_record = pd.DataFrame([{
        "docID": doc_id,
        "submitDateTime": submit_date,
        "errorMessage": error_msg,
        "timestamp": timestamp
    }])
    failed_log_path = Config.FAILED_LOG_PATH
    failed_record.to_csv(failed_log_path, mode='a', header=not failed_log_path.exists(), index=False, encoding='utf_8_sig')

def step3_execute_download(docs_to_download: pd.DataFrame):
    """
    ステップ③: 実際にファイルのダウンロードを実行し、年/四半期フォルダに保存する。
    """
    logging.info("--- ステップ③ ダウンロードの実行 ---")
    if docs_to_download.empty:
        logging.info("✅ ダウンロード対象の新しいファイルはありません。処理を完了します。")
        logging.info("-" * 40)
        return

    logging.info(f"{len(docs_to_download)}件のファイルのダウンロードを開始します。")

    for _, row in tqdm(docs_to_download.iterrows(), total=len(docs_to_download), desc="ZIPダウンロード進捗"):
        doc_id = row['docID']
        submit_date = row['submitDateTime']
        
        # --- ファイル整理のロジック ---
        success = download_single_file(doc_id, submit_date, Config.SAVE_FOLDER)
        if not success:
            log_failed_download(doc_id, submit_date, "初回ダウンロード失敗")

        time.sleep(0.1)

    logging.info("✅ ダウンロード処理が完了しました。")
    logging.info("-" * 40)

def retry_failed_downloads():
    """失敗したダウンロードを再試行し、成功したものはログから削除する"""
    failed_log_path = Config.FAILED_LOG_PATH

    if not failed_log_path.exists():
        logging.info("再試行対象の失敗ログは存在しません。")
        return

    try:
        failed_df = pd.read_csv(failed_log_path, encoding='utf_8_sig')
    except Exception as e:
        logging.error(f"失敗ログの読み込みに失敗しました: {e}")
        logging.debug(traceback.format_exc())
        return

    if failed_df.empty:
        logging.info("失敗ログは空です。")
        return

    logging.info(f"🔁 {len(failed_df)} 件の失敗ファイルを再試行します。")
    successful_ids = []
    failed_again = [] # 再失敗記録用

    for _, row in tqdm(failed_df.iterrows(), total=len(failed_df), desc="再試行中"):
        doc_id = row['docID']
        submit_date = pd.to_datetime(row['submitDateTime'], errors='coerce')

        success = download_single_file(doc_id, submit_date, Config.SAVE_FOLDER)

        if success:
            successful_ids.append(doc_id)
        else:
            logging.warning(f"再試行失敗: {doc_id}")
            failed_again.append((doc_id, submit_date))

        time.sleep(0.1)
        
    # 成功したIDをログから削除
    remaining_df = failed_df[~failed_df['docID'].isin(successful_ids)]
    remaining_df.to_csv(failed_log_path, index=False, encoding='utf_8_sig')

    # 再記録（失敗したものだけ）
    for doc_id, submit_date in failed_again:
        log_failed_download(doc_id, submit_date, "再試行失敗")

    logging.info(f"✅ 再試行完了。成功: {len(successful_ids)} 件 / 残り: {len(remaining_df) + len(failed_again)} 件")

def step_store_summary_to_db(summary_df: pd.DataFrame):
    """
    ステップ④: 取得したサマリーデータをSQLiteデータベースに保管する。
    テーブル名: edinet_document_summaries
    """
    logging.info("--- ステップ④ サマリーデータのSQLite保管 ---")
    if summary_df.empty:
        logging.warning("保管するサマリーデータがありません。")
        return

    conn = None
    try:
        conn = sqlite3.connect(Config.DB_PATH)
        logging.info(f"SQLiteデータベース '{Config.DB_PATH.name}' に接続しました。")

        # 提出書類一覧のJSON構造 [38-44] を考慮し、DataFrameをSQLiteに書き込み
        # docIDは一意なためプライマリキーとして設定
        summary_df.to_sql(
            "edinet_document_summaries",
            conn,
            if_exists='replace', # 毎回全件置き換え (運用に合わせて 'append' や 'upsert' を検討)
            index=False,
            dtype={
                'seqNumber': 'INTEGER',
                'docID': 'TEXT PRIMARY KEY', # docIDを主キーに設定
                'edinetCode': 'TEXT',
                'secCode': 'TEXT',
                'JCN': 'TEXT',
                'filerName': 'TEXT',
                'fundCode': 'TEXT',
                'ordinanceCode': 'TEXT',
                'formCode': 'TEXT',
                'docTypeCode': 'TEXT',
                'periodStart': 'TEXT',
                'periodEnd': 'TEXT',
                'submitDateTime': 'TIMESTAMP',
                'docDescription': 'TEXT',
                'issuerEdinetCode': 'TEXT',
                'subjectEdinetCode': 'TEXT',
                'subsidiaryEdinetCode': 'TEXT',
                'currentReportReason': 'TEXT',
                'parentDocID': 'TEXT',
                'opeDateTime': 'TIMESTAMP',
                'withdrawalStatus': 'TEXT',
                'docInfoEditStatus': 'TEXT',
                'disclosureStatus': 'TEXT',
                'xbrlFlag': 'TEXT',
                'pdfFlag': 'TEXT',
                'attachDocFlag': 'TEXT',
                'englishDocFlag': 'TEXT',
                'csvFlag': 'TEXT',
                'legalStatus': 'TEXT'
            }
        )
        logging.info(f"✅ サマリーデータを 'edinet_document_summaries' テーブルに保管しました（{len(summary_df)} 件）。")

    except sqlite3.Error as e:
        logging.error(f"SQLiteデータベース操作中にエラーが発生しました: {e}")
        logging.debug(traceback.format_exc())
    except Exception as e:
        logging.error(f"サマリーデータのSQLite保管中に予期せぬエラーが発生しました: {e}")
        logging.debug(traceback.format_exc())
    finally:
        if conn:
            conn.close()
            logging.info("SQLiteデータベース接続を閉じました。")
    logging.info("-" * 40)

def step_extract_and_index_csv(zip_base_folder: Path):
    """
    ステップ⑤: ダウンロード済みZIPファイルからCSVファイルを抽出し、そのパスをSQLiteに記録する。
    CSVファイルは一時抽出フォルダに保管される。
    テーブル名: edinet_extracted_csv_details
    """
    logging.info("--- ステップ⑤ CSV抽出と抽出パスのSQLite記録 ---")

    # 一時抽出フォルダを準備
    extract_temp_folder = Config.EXTRACTED_CSV_TEMP_FOLDER
    extract_temp_folder.mkdir(parents=True, exist_ok=True)

    all_zip_files = list(zip_base_folder.rglob('*.zip'))
    if not all_zip_files:
        logging.info("処理対象のZIPファイルが見つかりません。")
        return

    conn = None
    try:
        conn = sqlite3.connect(Config.DB_PATH)
        logging.info(f"SQLiteデータベース '{Config.DB_PATH.name}' に接続しました。")

        # CSV抽出情報のテーブルを作成（存在しない場合）
        conn.execute("""
            CREATE TABLE IF NOT EXISTS edinet_extracted_csv_details (
                docID TEXT NOT NULL,
                csv_filename TEXT NOT NULL,
                extracted_path TEXT PRIMARY KEY,
                extraction_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(docID) REFERENCES edinet_document_summaries(docID)
            )
        """)
        conn.commit()

        processed_zip_count = 0 # 処理したZIPファイルの数
        total_extracted_csv_count = 0 # 抽出したCSVファイルの総数
        inserted_path_count = 0 # DBに記録したCSVパスの総数

        for zip_file_path in tqdm(all_zip_files, desc="CSV抽出とDB記録"):
            doc_id = zip_file_path.stem # ZIPファイル名からdocIDを取得
            try:
                # 抽出先フォルダを docID ごとに分けることで、ファイルの衝突を防ぐ
                current_extract_folder = extract_temp_folder / doc_id
                
                extracted_csv_paths = extract_csv_from_zip(zip_file_path, current_extract_folder)

                if extracted_csv_paths:
                    processed_zip_count += 1
                    total_extracted_csv_count += len(extracted_csv_paths)

                    for csv_path in extracted_csv_paths:
                        # 抽出パスをデータベースに記録
                        conn.execute(
                            "INSERT OR REPLACE INTO edinet_extracted_csv_details (docID, csv_filename, extracted_path) VALUES (?, ?, ?)",
                            (doc_id, csv_path.name, str(csv_path))
                        )
                        inserted_path_count += 1
                    conn.commit() # トランザクションをコミット
                # else: extract_csv_from_zip 内で debug/warning が出力される

            except Exception as e:
                logging.error(f"ZIPファイル '{zip_file_path.name}' のCSV抽出・DB記録中にエラーが発生しました: {e}")
                logging.debug(traceback.format_exc())
        
        logging.info(
            f"✅ CSV抽出とSQLite記録処理が完了しました。"
            f"計 {processed_zip_count} 件のZIPファイルから {total_extracted_csv_count} 件のCSVを抽出し、"
            f"{inserted_path_count} 件のCSVパスをDBに記録しました。"
        )

    except sqlite3.Error as e:
        logging.error(f"SQLiteデータベース操作中にエラーが発生しました: {e}")
        logging.debug(traceback.format_exc())
    except Exception as e:
        logging.error(f"CSV抽出・DB記録処理中に予期せぬエラーが発生しました: {e}")
        logging.debug(traceback.format_exc())
    finally:
        if conn:
            conn.close()
            logging.info("SQLiteデータベース接続を閉じました。")
    
    # 必要に応じて一時抽出フォルダのクリーンアップを追加
    # 例: shutil.rmtree(extract_temp_folder)
    # ただし、後でCSVファイルの内容を分析するために残しておくことも多いので、ここでは自動削除はしない。

    logging.info("-" * 40)
```

### 毎回テーブルの削除＆新規作成を修正

edinet_steps.py

- 関数名をstep~をstep4~ step5~に変更
- 変更前
  - 毎回テーブル全体を削除し、新しいデータで再作成
- 変更後
  - データベーステーブルを毎回置き換えるのではなく、新しいレコードは追加し、既存のレコードは更新する (upsert) ように変更

```
def step4_store_summary_to_db(summary_df: pd.DataFrame):
    """
    ステップ④: 取得したサマリーデータをSQLiteデータベースに保管する。
    テーブル名: edinet_document_summaries
    """
    logging.info("--- ステップ④ サマリーデータのSQLite保管 ---")
    if summary_df.empty:
        logging.warning("保管するサマリーデータがありません。")
        return

    conn = None
    try:
        conn = sqlite3.connect(Config.DB_PATH)
        logging.info(f"SQLiteデータベース '{Config.DB_PATH.name}' に接続しました。")

        # 1. メインテーブルのスキーマを定義し、存在しない場合は作成する
        #    docIDは一意の識別子としてPRIMARY KEYに設定する
        columns_with_types = {
            'seqNumber': 'INTEGER',
            'docID': 'TEXT PRIMARY KEY', # docIDを主キーとして定義
            'edinetCode': 'TEXT',
            'secCode': 'TEXT',
            'JCN': 'TEXT',
            'filerName': 'TEXT',
            'fundCode': 'TEXT',
            'ordinanceCode': 'TEXT',
            'formCode': 'TEXT',
            'docTypeCode': 'TEXT',
            'periodStart': 'TEXT',
            'periodEnd': 'TEXT',
            'submitDateTime': 'TIMESTAMP',
            'docDescription': 'TEXT',
            'issuerEdinetCode': 'TEXT',
            'subjectEdinetCode': 'TEXT',
            'subsidiaryEdinetCode': 'TEXT',
            'currentReportReason': 'TEXT',
            'parentDocID': 'TEXT',
            'opeDateTime': 'TIMESTAMP',
            'withdrawalStatus': 'TEXT',
            'docInfoEditStatus': 'TEXT',
            'disclosureStatus': 'TEXT',
            'xbrlFlag': 'TEXT',
            'pdfFlag': 'TEXT',
            'attachDocFlag': 'TEXT',
            'englishDocFlag': 'TEXT',
            'csvFlag': 'TEXT',
            'legalStatus': 'TEXT'
        }
        
        create_table_sql_parts = [f"{col_name} {col_type}" for col_name, col_type in columns_with_types.items()]
        create_table_sql = f"CREATE TABLE IF NOT EXISTS edinet_document_summaries ({', '.join(create_table_sql_parts)})"
        conn.execute(create_table_sql)
        conn.commit()

        # 2. 現在のサマリーデータを一時テーブルに書き込む
        #    一時テーブルではdocIDをPRIMARY KEYにする必要はないが、型はメインテーブルに合わせる
        temp_dtype_map = {k: v.replace(' PRIMARY KEY', '') for k, v in columns_with_types.items()}
        summary_df.to_sql(
            "temp_edinet_document_summaries", # 一時テーブル名
            conn,
            if_exists='replace', # 一時テーブルは毎回置き換える
            index=False,
            dtype=temp_dtype_map
        )
        
        # 3. INSERT OR REPLACE を使って一時テーブルからメインテーブルへデータを移動する
        #    これにより、docIDが既存の場合はレコードが更新され、新しい場合は挿入される
        columns = ', '.join(summary_df.columns)
        conn.execute(f"""
            INSERT OR REPLACE INTO edinet_document_summaries ({columns})
            SELECT {columns} FROM temp_edinet_document_summaries
        """)
        conn.commit()

        # 4. 一時テーブルを削除する
        conn.execute("DROP TABLE temp_edinet_document_summaries")
        conn.commit()

        logging.info(f"✅ サマリーデータを 'edinet_document_summaries' テーブルに保管しました（{len(summary_df)} 件）。"
                     f"既存のレコードは更新され、新しいレコードが追加されました。")

    except sqlite3.Error as e:
        logging.error(f"SQLiteデータベース操作中にエラーが発生しました: {e}")
        logging.debug(traceback.format_exc())
    except Exception as e:
        logging.error(f"サマリーデータのSQLite保管中に予期せぬエラーが発生しました: {e}")
        logging.debug(traceback.format_exc())
    finally:
        if conn:
            conn.close()
            logging.info("SQLiteデータベース接続を閉じました。")
    logging.info("-" * 40)
```
