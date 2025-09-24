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
from sqlalchemy.dialects import sqlite
from sqlalchemy import text # text()関数を使用して、Core SQL操作を行う

# zip_utilsからCSV抽出関数をインポート
from .zip_utils import extract_csv_from_zip 
from .database_setup import Engine # データベースモジュールから Engine をインポート
from edinet_api import update_summary_file,download_single_file
from . import storage_repo
from . import file_processor

# urllib3のInsecureRequestWarningを非表示にする
warnings.filterwarnings('ignore', category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

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

def step5_store_summary_to_db(summary_df: pd.DataFrame):
    """
    ステップ④: 取得したサマリーデータをSQLiteデータベースに保管する。
    """
    logging.info("--- ステップ④ サマリーデータのSQLite保管 ---")
    
    # 処理を storage_repo に委譲する
    try:
        storage_repo.store_document_summaries(summary_df)
    except Exception:
        # エラーはリポジトリ側でロギングされているため、ここではフロー継続/停止を判断
        logging.error("ステップ④が失敗しました。")
        raise
    logging.info("-" * 40)
    
def step6_extract_and_index_csv(zip_base_folder: Path):
    """
    ステップ⑤: ダウンロード済みZIPファイルからCSVファイルを抽出し、そのパスをSQLiteに記録する。
    """
    logging.info("--- ステップ⑤ CSV抽出と抽出パスのSQLite記録 ---")
    # ファイル処理層に抽出と、リポジトリ層へのインデックス作成を依頼
    file_processor.extract_and_index_all_csvs(zip_base_folder, storage_repo)
    logging.info("-" * 40)

def step7_parse_and_store_csv_data_to_db():
    """
    ステップ⑦: 抽出されたCSVファイルを解析し、財務数値をSQLiteデータベースに保管する。
    """
    logging.info("--- ステップ⑦ CSV解析と財務数値のSQLite保管 ---")

    # 1. リポジトリから解析対象のCSVパスを取得
    csv_paths_df = file_processor.get_csv_paths_from_repo()
    
    # 2. ファイル処理層でCSVを解析し、整形されたDataFrameを取得
    financial_df = file_processor.parse_all_financial_csvs(csv_paths_df)

    # 3. リポジトリ層を使ってデータベースに保管
    if not financial_df.empty:
        storage_repo.store_financial_data(financial_df)
    logging.info("-" * 40)
