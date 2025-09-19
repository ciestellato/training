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

def step5_store_summary_to_db(summary_df: pd.DataFrame):
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
    
def step6_extract_and_index_csv(zip_base_folder: Path):
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

def step7_parse_and_store_csv_data_to_db():
    """
    ステップ⑦: 抽出されたCSVファイルを解析し、財務数値をSQLiteデータベースに保管する。
    テーブル名: edinet_financial_data (例)
    """
    logging.info("--- ステップ⑦ CSV解析と財務数値のSQLite保管 ---")

    conn = None
    try:
        conn = sqlite3.connect(Config.DB_PATH)
        logging.info(f"SQLiteデータベース '{Config.DB_PATH.name}' に接続しました。")

        # 財務データ格納用テーブルの作成（存在しない場合）
        # docID, secCode, fiscalYear, term, accountName の組み合わせを主キーにすることを検討
        conn.execute("""
            CREATE TABLE IF NOT EXISTS edinet_financial_data (
                docID TEXT NOT NULL,
                secCode TEXT,
                fiscalYear INTEGER,
                term TEXT,
                accountName TEXT NOT NULL,
                amount REAL,
                unit TEXT,
                currency TEXT,
                PRIMARY KEY (docID, accountName, fiscalYear, term),
                FOREIGN KEY(docID) REFERENCES edinet_document_summaries(docID)
            )
        """)
        conn.commit()

        # edinet_extracted_csv_details テーブルから、処理対象のCSVパスを取得
        # まだ解析されていないCSVファイルのみを対象とすることが望ましい
        # (例: 新しいフラグを edinet_extracted_csv_details に追加し、処理済みをマークするなど)
        csv_paths_df = pd.read_sql_query(
            "SELECT docID, extracted_path FROM edinet_extracted_csv_details", conn
        )

        if csv_paths_df.empty:
            logging.info("解析対象のCSVファイルパスが見つかりません。")
            return

        all_financial_data = []
        processed_csv_count = 0

        for _, row in tqdm(csv_paths_df.iterrows(), total=len(csv_paths_df), desc="CSVファイル解析"):
            doc_id = row['docID']
            csv_path = Path(row['extracted_path'])

            if not csv_path.exists():
                logging.warning(f"CSVファイルが存在しません: {csv_path}。スキップします。")
                continue

            try:
                # CSVファイルを読み込み、財務数値を解析するロジックをここに記述
                # 例: df_csv = pd.read_csv(csv_path)
                #    # EDINET CSVの構造に合わせてデータを抽出・整形
                #    # 例えば、特定の列を勘定科目、金額として抽出
                #    # temp_data = df_csv[['勘定科目名', '金額', '単位', '期間']]
                #    # temp_data['docID'] = doc_id
                #    # all_financial_data.append(temp_data)

                # ここでは具体的なCSVレイアウトが不明なため、ダミーデータを例示
                # 実際のEDINET CSVの構造に合わせて解析処理を実装してください。
                dummy_data = {
                    'docID': doc_id,
                    'secCode': 'xxxx', # docIDから取得する、またはedinet_document_summariesから結合
                    'fiscalYear': 2023,
                    'term': 'Annual',
                    'accountName': '売上高',
                    'amount': 100000000,
                    'unit': '円',
                    'currency': 'JPY'
                }
                all_financial_data.append(dummy_data)
                processed_csv_count += 1

            except Exception as e:
                logging.error(f"CSVファイル '{csv_path.name}' の解析中にエラーが発生しました: {e}")
                logging.debug(traceback.format_exc())

        if all_financial_data:
            financial_df = pd.DataFrame(all_financial_data)
            
            # DataFrameをSQLiteテーブルに格納 (INSERT OR REPLACEで重複を避け、更新)
            # if_exists='append' とし、INSERT OR REPLACE を直接SQLで実行する方が柔軟性があります
            # pandas.to_sql では if_exists='replace' または 'append' しか選べないため、
            # 独自のupsertロジックを実装するか、一時テーブル経由でINSERT OR REPLACEを行う
            # 前回の `step_store_summary_to_db` と同様の手法が利用可能です
            
            # --- Upsertロジックの例（前回のsummary_dfと同様） ---
            # 1. 一時テーブルに書き込む
            financial_df.to_sql(
                "temp_edinet_financial_data",
                conn,
                if_exists='replace',
                index=False,
                dtype={
                    'docID': 'TEXT',
                    'secCode': 'TEXT',
                    'fiscalYear': 'INTEGER',
                    'term': 'TEXT',
                    'accountName': 'TEXT',
                    'amount': 'REAL',
                    'unit': 'TEXT',
                    'currency': 'TEXT'
                }
            )
            # 2. INSERT OR REPLACE でメインテーブルへ移動
            columns = ', '.join(financial_df.columns)
            conn.execute(f"""
                INSERT OR REPLACE INTO edinet_financial_data ({columns})
                SELECT {columns} FROM temp_edinet_financial_data
            """)
            conn.commit()
            # 3. 一時テーブルを削除
            conn.execute("DROP TABLE temp_edinet_financial_data")
            conn.commit()
            # --- Upsertロジックの例 終了 ---

            logging.info(f"✅ {processed_csv_count} 件のCSVファイルを解析し、"
                         f"{len(financial_df)} 件の財務数値を 'edinet_financial_data' テーブルに保管しました。")
        else:
            logging.info("解析・保管された財務数値データはありません。")

    except sqlite3.Error as e:
        logging.error(f"SQLiteデータベース操作中にエラーが発生しました: {e}")
        logging.debug(traceback.format_exc())
    except Exception as e:
        logging.error(f"CSV解析と財務数値のSQLite保管中に予期せぬエラーが発生しました: {e}")
        logging.debug(traceback.format_exc())
    finally:
        if conn:
            conn.close()
            logging.info("SQLiteデータベース接続を閉じました。")
    logging.info("-" * 40)
