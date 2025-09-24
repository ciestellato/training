import pandas as pd
from pathlib import Path
import logging
import sqlite3
from tqdm import tqdm
from edinet_config import Config
from .zip_utils import extract_csv_from_zip # 既存のZIP抽出ユーティリティを利用

"""責任範囲：ローカルでのファイル操作やデータ解析。"""

# --- 1. ZIPからCSVを抽出する (旧 step6 のファイル操作ロジック) ---

def extract_and_index_all_csvs(zip_base_folder: Path, repo):
    """
    指定されたフォルダ内の全てのZIPからCSVを抽出し、パスをリポジトリ (DB) に記録する。
    repo は storage_repo.py モジュールを指すことを想定。
    """
    logging.info("--- CSV抽出処理を開始 ---")
    
    extract_temp_folder = Config.EXTRACTED_CSV_TEMP_FOLDER
    extract_temp_folder.mkdir(parents=True, exist_ok=True)

    all_zip_files = list(zip_base_folder.rglob('*.zip'))

    if not all_zip_files:
        logging.info("処理対象のZIPファイルが見つかりません。")
        return

    inserted_path_count = 0 
    
    for zip_file_path in tqdm(all_zip_files, desc="CSV抽出とDB記録"):
        doc_id = zip_file_path.stem 
        
        try:
            # 抽出を実行 [9]
            current_extract_folder = extract_temp_folder / doc_id
            extracted_csv_paths = extract_csv_from_zip(zip_file_path, current_extract_folder)

            if extracted_csv_paths:
                for csv_path in extracted_csv_paths:
                    # DBへの記録はリポジトリに委託
                    repo.index_extracted_csv_path(doc_id, csv_path.name, str(csv_path))
                    inserted_path_count += 1

        except Exception as e:
            logging.error(f"ZIPファイル '{zip_file_path.name}' のCSV抽出中にエラーが発生しました: {e}")
        
    logging.info(f"✅ CSV抽出とパス記録が完了しました。合計 {inserted_path_count} 件のCSVパスを記録。")


# --- 2. データベースから解析対象のCSVパスを読み込む ---

def get_csv_paths_from_repo() -> pd.DataFrame:
    """
    DB (edinet_extracted_csv_details) から解析対象のCSVパスを読み込む。
    """
    conn = None
    try:
        conn = sqlite3.connect(Config.DB_PATH)
        # 既存のステップ7のロジック [10] を流用
        csv_paths_df = pd.read_sql_query(
            "SELECT docID, extracted_path FROM edinet_extracted_csv_details", conn
        )
        return csv_paths_df
    except sqlite3.Error as e:
        logging.error(f"CSVパスの読み込み中にエラーが発生しました: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

# --- 3. CSVファイルを解析し、財務データDataFrameを生成する (旧 step7 の解析ロジック) ---

def parse_all_financial_csvs(csv_paths_df: pd.DataFrame) -> pd.DataFrame:
    """
    CSVパスリストに基づき、各CSVを解析して統合された財務データDataFrameを返す。
    """
    logging.info("--- CSV解析処理を開始 ---")

    if csv_paths_df.empty:
        logging.info("解析対象のCSVファイルパスが見つかりません。")
        return pd.DataFrame()

    all_financial_data = []
    
    # DBからsecCodeを事前に取得するための準備 (edinet_document_summariesテーブルから)
    conn = sqlite3.connect(Config.DB_PATH)
    summary_lookup_df = pd.read_sql_query("SELECT docID, secCode FROM edinet_document_summaries", conn)
    conn.close()
    
    summary_lookup = summary_lookup_df.set_index('docID')['secCode'].to_dict()

    for _, row in tqdm(csv_paths_df.iterrows(), total=len(csv_paths_df), desc="CSVファイル解析"):
        doc_id = row['docID']
        csv_path = Path(row['extracted_path'])
        
        if not csv_path.exists():
            logging.warning(f"CSVファイルが存在しません: {csv_path}。スキップします。")
            continue

        try:
            # 実際のEDINET CSVの構造に合わせて解析処理を実装
            
            # EDINETのCSVファイルは、XBRLから変換された形式（例: [11] のような要素IDベース）
            # または特定のレイアウトを持つもの [12] が存在します。
            
            # ここでは、外部ソースのXBRLデータ [11] の構造を参考に、
            # 必要な勘定科目（例: 売上高、資産合計）を抽出し、DataFrameを整形するロジックを実装する前提で、
            # サンプルデータの抽出処理を記述します。
            
            df_csv = pd.read_csv(csv_path, encoding='utf-16')
            
            # --- 分岐ロジック ---
            
            # 1. 監査報告書など、財務数値でないCSVファイルの除外 (または専用処理)
            # CSVファイル名には、XBRLタクソノミに基づき接頭辞が付与されていることが多い
            if csv_path.name.startswith("jpaud-"):
                # 監査報告書なので、財務数値抽出の対象外とする
                logging.debug(f"監査報告書ファイルを除外しました: {csv_path.name}")
                continue
                
            # 2. 財務数値CSVを処理
            if '要素ID' not in df_csv.columns:
                # 財務数値CSVだが、ヘッダーが想定外
                logging.warning(f"CSVファイル '{csv_path.name}' に '要素ID' カラムが見つかりません。")
                continue

            # --- 解析ダミーロジック ---
            # 実際のXBRL_TO_CSVは複雑なため、ここでは概念的なフィルタリングを示す
            # 外部ソースのデータ例 [11, 13] に基づき、勘定科目名と値、単位を抽出する
            
            # 抽出対象の要素IDのリスト (例: jppfs_cor:NetSales, jppfs_cor:Assets)
            target_element_ids = ['jpcrp_cor:NetSalesSummaryOfBusinessResults', 'jppfs_cor:Assets']
            
            extracted_records = df_csv[df_csv['要素ID'].isin(target_element_ids)].copy()
            
            if not extracted_records.empty:
                temp_data = extracted_records.rename(columns={
                    '項目名': 'accountName',
                    '値': 'amount',
                    '単位': 'unit'
                })
                # その他のメタ情報を付与
                temp_data['docID'] = doc_id
                temp_data['secCode'] = summary_lookup.get(doc_id)
                # 注: 期間の特定 (fiscalYear, term) は 'コンテキストID' や '期間・時点' 列から複雑なロジックで導出する必要があります。
                temp_data['fiscalYear'] = 9999 # 仮
                temp_data['term'] = 'Annual' # 仮
                temp_data['currency'] = temp_data['ユニットID'].apply(lambda x: 'JPY' if x == 'JPY' else None)
                
                # 必要なカラムのみに絞り込み
                final_cols = ['docID', 'secCode', 'fiscalYear', 'term', 'accountName', 'amount', 'unit', 'currency']
                all_financial_data.append(temp_data[final_cols])
            
            # --- 解析ダミーロジック 終了 ---

        except Exception as e:
            logging.error(f"CSVファイル '{csv_path.name}' の解析中にエラーが発生しました: {e}")
            logging.debug(e)
            continue
            
    if all_financial_data:
        return pd.concat(all_financial_data, ignore_index=True)
    else:
        return pd.DataFrame()